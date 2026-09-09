"""CodeSupply scan worker — processes scans through the complete pipeline."""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx
from sqlalchemy import select

from app.api.routes import _get_stages, _scan_to_response
from app.api.ws import manager
from app.core.config import Settings, get_settings
from app.core.database import async_session_factory, init_db
from app.models.models import (
    Component,
    DependencyEdge,
    Evidence,
    ExternalLookupStatus,
    Manifest,
    RiskReason,
    SBOMValidationResult,
    Scan,
    ScanStage,
    VulnerabilityFinding,
)
from app.models.models import (
    VulnerabilityCache as VulnerabilityCacheModel,
)
from app.risk.engine import RiskEngine
from app.sbom.generator import CycloneDXGenerator
from app.sbom.validator import SBOMValidator
from app.scanners.discovery import discover_manifests
from app.scanners.go.parser import GoParser
from app.scanners.maven.parser import MavenParser
from app.scanners.npm.parser import NpmParser
from app.scanners.python.parser import PythonParser
from app.scanners.rust.parser import RustParser
from app.services.archive import ArchiveService
from app.services.normalizer import ComponentNormalizer, ParsedPackage
from app.services.relationships import RelationshipBuilder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("codesupply.worker")


class ScanWorker:
    """Processes scan jobs through the complete pipeline."""

    STAGES = [
        "extracting",
        "discovering",
        "parsing",
        "normalizing",
        "resolving",
        "sbom_generation",
        "sbom_validation",
        "vulnerability_analysis",
        "risk_analysis",
    ]

    def __init__(self, settings: Settings):
        self.settings = settings
        self.archive_service = ArchiveService(settings)
        self.npm_parser = NpmParser()
        self.python_parser = PythonParser()
        self.maven_parser = MavenParser()
        self.go_parser = GoParser()
        self.rust_parser = RustParser()
        self.normalizer = ComponentNormalizer()
        self.relationship_builder = RelationshipBuilder()
        self.sbom_generator = CycloneDXGenerator()
        self.sbom_validator = SBOMValidator()
        self.risk_engine = RiskEngine()

    async def _broadcast_scan(self, db, scan_id: str):
        try:
            # We must commit before reading to ensure latest state? No, we just modified the objects, but let's refresh or fetch.
            # actually we can just select it
            result = await db.execute(select(Scan).where(Scan.id == scan_id))
            scan = result.scalar_one_or_none()
            if scan:
                stages = await _get_stages(scan_id, db)
                response = _scan_to_response(scan, stages)
                await manager.broadcast_scan_update(scan_id, response.model_dump(mode="json"))
        except Exception as e:
            logger.error(f"WS Broadcast error: {e}")

    async def _update_stage(
        self,
        db,
        scan_id: str,
        stage_name: str,
        status: str,
        message: str = None,
        completed: int = None,
        total: int = None,
    ):
        """Create or update a scan stage record."""
        # Check if stage exists
        result = await db.execute(
            select(ScanStage).where(
                ScanStage.scan_id == scan_id,
                ScanStage.stage_name == stage_name,
            )
        )
        stage = result.scalar_one_or_none()

        if stage:
            stage.status = status
            stage.message = message
            if completed is not None:
                stage.completed_count = completed
            if total is not None:
                stage.total_count = total
            if status == "completed":
                stage.completed_at = datetime.now(timezone.utc)
        else:
            stage = ScanStage(
                id=uuid.uuid4().hex,
                scan_id=scan_id,
                stage_name=stage_name,
                status=status,
                message=message,
                completed_count=completed,
                total_count=total,
                started_at=datetime.now(timezone.utc),
            )
            db.add(stage)

        await db.commit()
        await self._broadcast_scan(db, scan_id)

    async def process_scan(self, scan_id: str):
        """Process a scan through all pipeline stages."""
        logger.info(f"Starting scan processing: {scan_id}")

        async with async_session_factory() as db:
            result = await db.execute(select(Scan).where(Scan.id == scan_id))
            scan = result.scalar_one_or_none()
            if not scan or scan.status != "queued":
                return

            scan.status = "extracting"
            scan.started_at = datetime.now(timezone.utc)
            await db.commit()
            await self._broadcast_scan(db, scan_id)

            extraction_path = None
            all_parsed_packages: list[ParsedPackage] = []
            all_parsed_relationships = []
            all_components: list[Component] = []
            all_edges: list[DependencyEdge] = []
            component_map: dict[str, str] = {}  # normalized_name -> component_id

            try:
                # ── STAGE 1: EXTRACTING ──────────────────────────────────
                await self._update_stage(
                    db,
                    scan_id,
                    "extracting",
                    "running",
                    "Validating and extracting archive",
                )

                upload_dir = Path(self.settings.TEMP_DIR) / scan_id
                zip_files = list(upload_dir.glob("*.zip"))
                if not zip_files:
                    raise ValueError("No ZIP file found for this scan")

                extraction_path = await self.archive_service.validate_and_extract(zip_files[0], scan_id)

                await self._update_stage(
                    db,
                    scan_id,
                    "extracting",
                    "completed",
                    "Archive extracted successfully",
                )
                logger.info(f"scan_extracted: {scan_id}")

                # ── STAGE 2: DISCOVERING ─────────────────────────────────
                scan.status = "discovering"
                await db.commit()
                await self._broadcast_scan(db, scan_id)
                await self._update_stage(db, scan_id, "discovering", "running", "Scanning for manifest files")

                discovered = discover_manifests(extraction_path)

                # Store manifest records
                for m in discovered:
                    manifest = Manifest(
                        id=uuid.uuid4().hex,
                        scan_id=scan_id,
                        file_path=m.path,
                        ecosystem=m.ecosystem,
                        manifest_type=m.manifest_type,
                        is_parseable=m.is_supported,
                        file_size=m.file_size,
                    )
                    db.add(manifest)

                scan.total_manifests = len(discovered)
                await db.commit()
                await self._broadcast_scan(db, scan_id)

                supported = [m for m in discovered if m.is_supported]
                await self._update_stage(
                    db,
                    scan_id,
                    "discovering",
                    "completed",
                    f"Found {len(discovered)} manifests ({len(supported)} supported)",
                    completed=len(discovered),
                    total=len(discovered),
                )
                logger.info(f"scan_discovered: {scan_id}, manifests={len(discovered)}")

                # ── STAGE 3: PARSING ─────────────────────────────────────
                scan.status = "parsing"
                await db.commit()
                await self._broadcast_scan(db, scan_id)
                await self._update_stage(db, scan_id, "parsing", "running", "Parsing manifest files")

                npm_declarations = []
                npm_lockfile_pkgs = []
                npm_lockfile_rels = []
                parsed_count = 0

                for m in supported:
                    file_path = extraction_path / m.path
                    if not file_path.exists():
                        continue

                    content = file_path.read_text(encoding="utf-8", errors="replace")

                    file_name = Path(m.path).name
                    if m.ecosystem == "npm":
                        if file_name == "package.json":
                            pkgs, rels = self.npm_parser.parse_package_json(content, m.path)
                            npm_declarations.extend(pkgs)
                            all_parsed_relationships.extend(rels)
                        elif file_name == "package-lock.json":
                            pkgs, rels = self.npm_parser.parse_package_lock(content, m.path)
                            npm_lockfile_pkgs.extend(pkgs)
                            npm_lockfile_rels.extend(rels)

                    elif m.ecosystem == "python":
                        if file_name == "requirements.txt":
                            pkgs = self.python_parser.parse_requirements_txt(content, m.path)
                            all_parsed_packages.extend(pkgs)
                        elif file_name == "pyproject.toml":
                            pkgs = self.python_parser.parse_pyproject_toml(content, m.path)
                            all_parsed_packages.extend(pkgs)

                    elif m.ecosystem == "maven":
                        if file_name == "pom.xml":
                            pkgs = self.maven_parser.parse_pom_xml(content, m.path)
                            all_parsed_packages.extend(pkgs)

                    elif m.ecosystem == "golang":
                        if file_name == "go.mod":
                            pkgs, rels = self.go_parser.parse_go_mod(content, m.path)
                            all_parsed_packages.extend(pkgs)
                            all_parsed_relationships.extend(rels)

                    elif m.ecosystem == "cargo":
                        if file_name == "Cargo.toml":
                            pkgs = self.rust_parser.parse_cargo_toml(content, m.path)
                            all_parsed_packages.extend(pkgs)

                    parsed_count += 1
                    await self._update_stage(
                        db,
                        scan_id,
                        "parsing",
                        "running",
                        f"Parsed {parsed_count}/{len(supported)} manifests",
                        completed=parsed_count,
                        total=len(supported),
                    )

                # Merge npm declarations with lockfile
                if npm_lockfile_pkgs:
                    merged_pkgs, merged_rels = self.npm_parser.merge_declarations_with_lockfile(
                        npm_declarations, npm_lockfile_pkgs, npm_lockfile_rels
                    )
                    all_parsed_packages.extend(merged_pkgs)
                    all_parsed_relationships.extend(merged_rels)
                else:
                    all_parsed_packages.extend(npm_declarations)

                await self._update_stage(
                    db,
                    scan_id,
                    "parsing",
                    "completed",
                    f"Parsed {parsed_count} manifests, found {len(all_parsed_packages)} packages",
                    completed=parsed_count,
                    total=len(supported),
                )
                logger.info(f"scan_parsed: {scan_id}, packages={len(all_parsed_packages)}")

                # ── STAGE 4: NORMALIZING ─────────────────────────────────
                scan.status = "normalizing"
                await db.commit()
                await self._broadcast_scan(db, scan_id)
                await self._update_stage(db, scan_id, "normalizing", "running", "Normalizing components")

                for i, pkg in enumerate(all_parsed_packages):
                    comp_data, evidences = self.normalizer.normalize(pkg, scan_id)
                    component = Component(
                        id=comp_data["id"],
                        scan_id=scan_id,
                        name=comp_data["name"],
                        version=comp_data["version"],
                        ecosystem=comp_data["ecosystem"],
                        package_manager=comp_data["package_manager"],
                        dependency_type=comp_data["dependency_type"],
                        source_file=comp_data["source_file"],
                        source_location=comp_data["source_location"],
                        version_confidence=comp_data["version_confidence"],
                        purl=comp_data["purl"],
                        original_declaration=comp_data["original_declaration"],
                        normalized_name=comp_data["normalized_name"],
                        risk_level="unknown",
                        license=comp_data.get("license"),
                    )
                    db.add(component)
                    all_components.append(component)
                    component_map[component.normalized_name] = component.id

                    # Store evidence
                    for ev in evidences:
                        evidence = Evidence(
                            id=uuid.uuid4().hex,
                            scan_id=scan_id,
                            component_id=component.id,
                            source_file=ev["source_file"],
                            source_location=ev.get("source_location"),
                            method=ev["method"],
                            confidence=ev["confidence"],
                            value=ev["value"],
                            evidence_type=ev["evidence_type"],
                        )
                        db.add(evidence)

                scan.total_components = len(all_components)
                await db.commit()
                await self._broadcast_scan(db, scan_id)

                await self._update_stage(
                    db,
                    scan_id,
                    "normalizing",
                    "completed",
                    f"Normalized {len(all_components)} components",
                    completed=len(all_components),
                    total=len(all_components),
                )

                # ── STAGE 5: RESOLVING ───────────────────────────────────
                scan.status = "resolving"
                await db.commit()
                await self._broadcast_scan(db, scan_id)
                await self._update_stage(
                    db,
                    scan_id,
                    "resolving",
                    "running",
                    "Building dependency relationships",
                )

                edges, edge_evidences = self.relationship_builder.build_edges(
                    all_parsed_relationships, component_map, scan_id
                )

                for edge_data in edges:
                    edge = DependencyEdge(
                        id=edge_data["id"],
                        scan_id=scan_id,
                        source_component_id=edge_data["source_component_id"],
                        target_component_id=edge_data["target_component_id"],
                        relationship_type=edge_data["relationship_type"],
                        confidence=edge_data["confidence"],
                        source_file=edge_data["source_file"],
                        evidence_method=edge_data["evidence_method"],
                    )
                    db.add(edge)
                    all_edges.append(edge)

                for ev in edge_evidences:
                    evidence = Evidence(
                        id=uuid.uuid4().hex,
                        scan_id=scan_id,
                        edge_id=ev.get("edge_id"),
                        source_file=ev["source_file"],
                        source_location=ev.get("source_location"),
                        method=ev["method"],
                        confidence=ev["confidence"],
                        value=ev["value"],
                        evidence_type=ev["evidence_type"],
                    )
                    db.add(evidence)

                await db.commit()
                await self._broadcast_scan(db, scan_id)

                await self._update_stage(
                    db,
                    scan_id,
                    "resolving",
                    "completed",
                    f"Built {len(all_edges)} dependency edges",
                    completed=len(all_edges),
                    total=len(all_edges),
                )

                # ── STAGE 6: SBOM GENERATION ─────────────────────────────
                scan.status = "sbom_generation"
                await db.commit()
                await self._broadcast_scan(db, scan_id)
                await self._update_stage(
                    db,
                    scan_id,
                    "sbom_generation",
                    "running",
                    "Generating CycloneDX SBOM",
                )

                sbom_dict = self.sbom_generator.generate(scan, all_components, all_edges)

                await self._update_stage(
                    db,
                    scan_id,
                    "sbom_generation",
                    "completed",
                    "CycloneDX 1.7 SBOM generated",
                )

                # ── STAGE 7: SBOM VALIDATION ─────────────────────────────
                scan.status = "sbom_validation"
                await db.commit()
                await self._broadcast_scan(db, scan_id)
                await self._update_stage(db, scan_id, "sbom_validation", "running", "Validating SBOM")

                validation = self.sbom_validator.validate(sbom_dict)

                val_record = SBOMValidationResult(
                    id=uuid.uuid4().hex,
                    scan_id=scan_id,
                    is_valid=validation.is_valid,
                    format="CycloneDX",
                    spec_version="1.7",
                    errors=validation.errors,
                    warnings=validation.warnings,
                    validated_at=datetime.now(timezone.utc),
                )
                db.add(val_record)
                await db.commit()
                await self._broadcast_scan(db, scan_id)

                status_msg = (
                    "✓ Valid CycloneDX document"
                    if validation.is_valid
                    else f"Validation failed: {len(validation.errors)} errors"
                )
                await self._update_stage(db, scan_id, "sbom_validation", "completed", status_msg)

                # ── STAGE 8: VULNERABILITY ANALYSIS ──────────────────────
                scan.status = "vulnerability_analysis"
                await db.commit()
                await self._broadcast_scan(db, scan_id)
                await self._update_stage(
                    db,
                    scan_id,
                    "vulnerability_analysis",
                    "running",
                    "Checking package versions against advisory intelligence",
                    completed=0,
                    total=len(all_components),
                )

                findings = []
                checked = 0
                unavailable_count = 0

                vuln_details_cache: dict[str, dict] = {}

                async def get_full_vuln_data(raw_vuln: dict) -> dict:
                    vuln_id = raw_vuln.get("id")
                    if not vuln_id:
                        return raw_vuln
                    if "severity" in raw_vuln or "database_specific" in raw_vuln or "summary" in raw_vuln:
                        return raw_vuln
                    if vuln_id in vuln_details_cache:
                        return vuln_details_cache[vuln_id]
                    try:
                        resp = await http_client.get(f"{self.settings.OSV_API_URL}/v1/vulns/{vuln_id}", timeout=10.0)
                        if resp.status_code == 200:
                            data = resp.json()
                            vuln_details_cache[vuln_id] = data
                            return data
                    except Exception as e:
                        logger.warning(f"Could not fetch full advisory {vuln_id}: {e}")
                    return raw_vuln

                async with httpx.AsyncClient(timeout=30.0) as http_client:
                    # Build batch queries for components with exact versions
                    queries = []
                    queryable_components = []

                    for comp in all_components:
                        if not comp.version or comp.version_confidence not in ("exact",):
                            # Mark as not applicable
                            lookup = ExternalLookupStatus(
                                id=uuid.uuid4().hex,
                                scan_id=scan_id,
                                component_id=comp.id,
                                service="osv",
                                status="not_applicable",
                            )
                            db.add(lookup)
                            checked += 1
                            continue

                        # Check cache first
                        ecosystem_mapped = {
                            "npm": "npm",
                            "pypi": "PyPI",
                            "maven": "Maven",
                            "golang": "Go",
                            "cargo": "crates.io",
                        }.get(comp.ecosystem, comp.ecosystem)

                        cache_result = await db.execute(
                            select(VulnerabilityCacheModel).where(
                                VulnerabilityCacheModel.ecosystem == ecosystem_mapped,
                                VulnerabilityCacheModel.package_name == comp.name,
                                VulnerabilityCacheModel.package_version == comp.version,
                            )
                        )
                        cached = cache_result.scalar_one_or_none()

                        if cached:
                            # Use cached data
                            cached_vulns = cached.response_data.get("vulns", []) if cached.response_data else []
                            for vuln_data in cached_vulns:
                                full_vuln = await get_full_vuln_data(vuln_data)
                                finding = self._create_finding(comp, full_vuln, scan_id)
                                db.add(finding)
                                findings.append(finding)

                            lookup = ExternalLookupStatus(
                                id=uuid.uuid4().hex,
                                scan_id=scan_id,
                                component_id=comp.id,
                                service="osv",
                                status="cached",
                                cached_at=cached.retrieved_at,
                            )
                            db.add(lookup)
                            checked += 1
                            continue

                        query = {
                            "package": {
                                "name": comp.name,
                                "ecosystem": ecosystem_mapped,
                            },
                            "version": comp.version,
                        }
                        queries.append(query)
                        queryable_components.append(comp)

                    # Batch query OSV
                    batch_size = self.settings.OSV_BATCH_SIZE
                    for batch_start in range(0, len(queries), batch_size):
                        batch_queries = queries[batch_start : batch_start + batch_size]
                        batch_comps = queryable_components[batch_start : batch_start + batch_size]

                        try:
                            resp = await http_client.post(
                                f"{self.settings.OSV_API_URL}/v1/querybatch",
                                json={"queries": batch_queries},
                            )
                            resp.raise_for_status()
                            results = resp.json().get("results", [])

                            for comp, result in zip(batch_comps, results):
                                vulns = result.get("vulns", [])
                                ecosystem_mapped = {
                                    "npm": "npm",
                                    "pypi": "PyPI",
                                    "maven": "Maven",
                                    "golang": "Go",
                                    "cargo": "crates.io",
                                }.get(comp.ecosystem, comp.ecosystem)

                                # Cache the result
                                cache_entry = VulnerabilityCacheModel(
                                    id=uuid.uuid4().hex,
                                    ecosystem=ecosystem_mapped,
                                    package_name=comp.name,
                                    package_version=comp.version,
                                    purl=comp.purl,
                                    response_data=result,
                                    source="osv",
                                )
                                db.add(cache_entry)

                                for vuln_data in vulns:
                                    full_vuln = await get_full_vuln_data(vuln_data)
                                    finding = self._create_finding(comp, full_vuln, scan_id)
                                    db.add(finding)
                                    findings.append(finding)

                                lookup = ExternalLookupStatus(
                                    id=uuid.uuid4().hex,
                                    scan_id=scan_id,
                                    component_id=comp.id,
                                    service="osv",
                                    status="checked",
                                )
                                db.add(lookup)
                                checked += 1

                        except Exception as e:
                            logger.error(f"OSV batch query failed: {e}")
                            for comp in batch_comps:
                                lookup = ExternalLookupStatus(
                                    id=uuid.uuid4().hex,
                                    scan_id=scan_id,
                                    component_id=comp.id,
                                    service="osv",
                                    status="unavailable",
                                    error_message=str(e)[:500],
                                )
                                db.add(lookup)
                                unavailable_count += 1
                                checked += 1

                        await self._update_stage(
                            db,
                            scan_id,
                            "vulnerability_analysis",
                            "running",
                            f"Checked {checked}/{len(all_components)} components",
                            completed=checked,
                            total=len(all_components),
                        )

                scan.total_vulnerabilities = len(findings)
                await db.commit()
                await self._broadcast_scan(db, scan_id)

                status_msg = f"Found {len(findings)} vulnerabilities across {checked} components"
                if unavailable_count > 0:
                    status_msg += f" ({unavailable_count} components could not be checked)"
                await self._update_stage(
                    db,
                    scan_id,
                    "vulnerability_analysis",
                    "completed",
                    status_msg,
                    completed=checked,
                    total=len(all_components),
                )

                # ── STAGE 9: RISK ANALYSIS ───────────────────────────────
                scan.status = "risk_analysis"
                await db.commit()
                await self._broadcast_scan(db, scan_id)
                await self._update_stage(
                    db,
                    scan_id,
                    "risk_analysis",
                    "running",
                    "Calculating risk scores",
                    completed=0,
                    total=len(all_components),
                )

                for i, comp in enumerate(all_components):
                    # Get vulnerabilities for this component
                    comp_vulns_result = await db.execute(
                        select(VulnerabilityFinding).where(VulnerabilityFinding.component_id == comp.id)
                    )
                    comp_vulns = comp_vulns_result.scalars().all()

                    # Get lookup status
                    lookup_result = await db.execute(
                        select(ExternalLookupStatus).where(
                            ExternalLookupStatus.component_id == comp.id,
                            ExternalLookupStatus.scan_id == scan_id,
                        )
                    )
                    lookup = lookup_result.scalar_one_or_none()
                    lookup_status = lookup.status if lookup else "unknown"

                    # Assess risk
                    assessment = self.risk_engine.assess_component(comp, list(comp_vulns), lookup_status)

                    # Update component
                    comp.risk_level = assessment.risk_level
                    comp.risk_score = assessment.risk_score

                    # Store risk reasons
                    for reason in assessment.reasons:
                        rr = RiskReason(
                            id=uuid.uuid4().hex,
                            scan_id=scan_id,
                            component_id=comp.id,
                            reason_type=reason.reason_type,
                            description=reason.description,
                            severity_contribution=reason.severity_contribution,
                        )
                        db.add(rr)

                    if (i + 1) % 10 == 0:
                        await self._update_stage(
                            db,
                            scan_id,
                            "risk_analysis",
                            "running",
                            f"Assessed {i + 1}/{len(all_components)} components",
                            completed=i + 1,
                            total=len(all_components),
                        )

                await db.commit()
                await self._broadcast_scan(db, scan_id)
                await self._update_stage(
                    db,
                    scan_id,
                    "risk_analysis",
                    "completed",
                    f"Risk analysis complete for {len(all_components)} components",
                    completed=len(all_components),
                    total=len(all_components),
                )

                # ── COMPLETE ─────────────────────────────────────────────
                scan.status = "complete"
                scan.completed_at = datetime.now(timezone.utc)
                await db.commit()
                await self._broadcast_scan(db, scan_id)

                logger.info(
                    f"scan_completed: {scan_id}, "
                    f"components={len(all_components)}, "
                    f"vulnerabilities={len(findings)}, "
                    f"edges={len(all_edges)}"
                )

            except Exception as e:
                logger.exception(f"scan_failed: {scan_id}")
                scan.status = "failed"
                scan.error_message = str(e)[:1000]
                scan.error_code = type(e).__name__
                await db.commit()
                await self._broadcast_scan(db, scan_id)

            finally:
                # Cleanup extraction directory (keep upload for retry)
                if extraction_path and extraction_path.exists():
                    import shutil

                    try:
                        shutil.rmtree(extraction_path)
                    except Exception:
                        pass

    def _create_finding(self, comp: Component, vuln_data: dict, scan_id: str) -> VulnerabilityFinding:
        """Create a VulnerabilityFinding from OSV vulnerability data."""
        vuln_id = vuln_data.get("id", "UNKNOWN")
        aliases = vuln_data.get("aliases", [])
        summary = vuln_data.get("summary", "")
        references = [ref.get("url", "") for ref in vuln_data.get("references", []) if ref.get("url")]

        # Extract severity via multiple strategies
        severity, cvss_score, cvss_vector = self._extract_severity(vuln_data)

        # Extract affected range and fixed version
        affected_range = None
        fixed_version = None
        affected_list = vuln_data.get("affected", [])
        for affected in affected_list:
            ranges = affected.get("ranges", [])
            for r in ranges:
                events = r.get("events", [])
                introduced = None
                fixed = None
                for event in events:
                    if "introduced" in event:
                        introduced = event["introduced"]
                    if "fixed" in event:
                        fixed = event["fixed"]
                if introduced is not None:
                    affected_range = f">={introduced}" if introduced != "0" else "all versions"
                    if fixed:
                        affected_range += f", <{fixed}"
                if fixed:
                    fixed_version = fixed

        # Parse modified date
        modified_at = None
        modified_str = vuln_data.get("modified")
        if modified_str:
            try:
                modified_at = datetime.fromisoformat(modified_str.replace("Z", "+00:00"))
            except Exception:
                pass

        return VulnerabilityFinding(
            id=uuid.uuid4().hex,
            scan_id=scan_id,
            component_id=comp.id,
            vuln_id=vuln_id,
            aliases=aliases,
            summary=summary,
            severity=severity,
            affected_range=affected_range,
            fixed_version=fixed_version,
            references=references,
            source="osv",
            modified_at=modified_at,
            cvss_score=cvss_score,
            cvss_vector=cvss_vector,
        )

    def _extract_severity(self, vuln_data: dict) -> tuple[str, float | None, str | None]:
        """Extract severity from OSV data using multiple strategies.

        Strategy order:
        1. Parse CVSS v3 vector string from severity[] array → compute base score
        2. Check database_specific.severity or database_specific.cvss for explicit label
        3. Check ecosystem_specific severity fields
        4. Infer from aliases (GHSA severity pattern)
        5. Default to "unknown"

        Returns:
            (severity_label, cvss_score, cvss_vector)
        """
        # Strategy 1: CVSS v3 vector from severity array
        severity_list = vuln_data.get("severity", [])
        for sev in severity_list:
            if sev.get("type") == "CVSS_V3":
                vector = sev.get("score", "")
                if vector and "/" in vector:
                    score = self._compute_cvss3_base_score(vector)
                    if score is not None:
                        return self._score_to_severity(score), score, vector

            # Some entries use CVSS_V2 — less precise but still useful
            if sev.get("type") == "CVSS_V2":
                vector = sev.get("score", "")
                if vector:
                    # Try to extract score from AV:x style — rough heuristic
                    score = self._estimate_cvss2_score(vector)
                    if score is not None:
                        return self._score_to_severity(score), score, vector

        # Strategy 2: database_specific fields
        db_specific = vuln_data.get("database_specific", {})
        if db_specific:
            # GitHub Advisory format
            ghsa_severity = db_specific.get("severity")
            if isinstance(ghsa_severity, str) and ghsa_severity.upper() in (
                "CRITICAL",
                "HIGH",
                "MODERATE",
                "MEDIUM",
                "LOW",
            ):
                label = ghsa_severity.upper()
                if label == "MODERATE":
                    label = "MEDIUM"
                return label.lower(), None, None

            # Some databases include cvss_score directly
            cvss_val = db_specific.get("cvss", {})
            if isinstance(cvss_val, dict):
                score = cvss_val.get("score") or cvss_val.get("baseScore")
                if isinstance(score, (int, float)):
                    return self._score_to_severity(float(score)), float(score), cvss_val.get("vectorString")

        # Strategy 3: Check affected[].ecosystem_specific
        for affected in vuln_data.get("affected", []):
            eco_specific = affected.get("ecosystem_specific", {})
            if isinstance(eco_specific, dict):
                sev = eco_specific.get("severity")
                if isinstance(sev, str) and sev.upper() in ("CRITICAL", "HIGH", "MODERATE", "MEDIUM", "LOW"):
                    label = sev.upper()
                    if label == "MODERATE":
                        label = "MEDIUM"
                    return label.lower(), None, None

        # Strategy 4: Infer from aliases (GHSA IDs sometimes follow severity patterns)
        # If we have any alias, at least mark as "medium" rather than "unknown"
        aliases = vuln_data.get("aliases", [])
        if aliases:
            # If there's a CVE, we know it's a real vulnerability — default to medium
            for alias in aliases:
                if alias.startswith("CVE-"):
                    return "medium", None, None

        # Strategy 5: If we have affected ranges, it's a real vuln — don't call it unknown
        if vuln_data.get("affected"):
            return "medium", None, None

        return "unknown", None, None

    @staticmethod
    def _score_to_severity(score: float) -> str:
        """Map CVSS score to severity label per CVSS v3 spec."""
        if score >= 9.0:
            return "critical"
        elif score >= 7.0:
            return "high"
        elif score >= 4.0:
            return "medium"
        elif score >= 0.1:
            return "low"
        return "none"

    @staticmethod
    def _compute_cvss3_base_score(vector: str) -> float | None:
        """Compute CVSS v3.x base score from a vector string.

        Implements the CVSS v3.1 base score algorithm per NIST SP 800-126.
        Vector format: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H

        Returns the base score (0.0–10.0) or None if the vector is invalid.
        """
        # Parse metrics from vector
        metrics: dict[str, str] = {}
        parts = vector.split("/")
        for part in parts:
            if ":" in part and not part.startswith("CVSS:"):
                key, val = part.split(":", 1)
                metrics[key] = val

        required = {"AV", "AC", "PR", "UI", "S", "C", "I", "A"}
        if not required.issubset(metrics.keys()):
            return None

        # Attack Vector
        av_scores = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.20}
        # Attack Complexity
        ac_scores = {"L": 0.77, "H": 0.44}
        # User Interaction
        ui_scores = {"N": 0.85, "R": 0.62}
        # Scope
        scope_changed = metrics["S"] == "C"

        # Privileges Required (depends on Scope)
        if scope_changed:
            pr_scores = {"N": 0.85, "L": 0.68, "H": 0.50}
        else:
            pr_scores = {"N": 0.85, "L": 0.62, "H": 0.27}

        # Impact metrics
        cia_scores = {"H": 0.56, "L": 0.22, "N": 0.0}

        try:
            av = av_scores[metrics["AV"]]
            ac = ac_scores[metrics["AC"]]
            pr = pr_scores[metrics["PR"]]
            ui = ui_scores[metrics["UI"]]
            c = cia_scores[metrics["C"]]
            i = cia_scores[metrics["I"]]
            a = cia_scores[metrics["A"]]
        except KeyError:
            return None

        # Exploitability sub-score
        exploitability = 8.22 * av * ac * pr * ui

        # Impact sub-score
        isc_base = 1.0 - ((1.0 - c) * (1.0 - i) * (1.0 - a))

        if isc_base <= 0:
            return 0.0

        if scope_changed:
            impact = 7.52 * (isc_base - 0.029) - 3.25 * (isc_base - 0.02) ** 15
        else:
            impact = 6.42 * isc_base

        if impact <= 0:
            return 0.0

        if scope_changed:
            base = min(1.08 * (impact + exploitability), 10.0)
        else:
            base = min(impact + exploitability, 10.0)

        # Round up to 1 decimal place (CVSS spec: "round up")
        import math

        return math.ceil(base * 10) / 10

    @staticmethod
    def _estimate_cvss2_score(vector: str) -> float | None:
        """Rough CVSS v2 score estimate from a vector string.

        Not a full implementation — provides a reasonable approximation
        for severity classification when CVSS v3 is unavailable.
        """
        metrics: dict[str, str] = {}
        for part in vector.split("/"):
            if ":" in part:
                key, val = part.split(":", 1)
                metrics[key] = val

        if "AV" not in metrics:
            return None

        # Rough scoring based on key metrics
        score = 5.0  # baseline
        av = metrics.get("AV", "N")
        ac = metrics.get("AC", "M")
        au = metrics.get("Au", "N")

        if av == "N":
            score += 1.5
        if ac == "L":
            score += 1.0
        if au == "N":
            score += 0.5

        c = metrics.get("C", "N")
        i = metrics.get("I", "N")
        a = metrics.get("A", "N")

        for metric_val in [c, i, a]:
            if metric_val == "C":
                score += 0.7
            elif metric_val == "P":
                score += 0.3

        return min(round(score, 1), 10.0)

    async def run_loop(self):
        """Poll for queued scans and process them."""
        logger.info("CodeSupply scan worker started")

        while True:
            try:
                async with async_session_factory() as db:
                    result = await db.execute(
                        select(Scan).where(Scan.status == "queued").order_by(Scan.created_at).limit(1)
                    )
                    scan = result.scalar_one_or_none()

                    if scan:
                        logger.info(f"Processing queued scan: {scan.id}")
                        await self.process_scan(scan.id)
                    else:
                        await asyncio.sleep(2)

            except Exception as e:
                logger.exception(f"Worker loop error: {e}")
                await asyncio.sleep(5)


async def main():
    """Worker entry point."""
    await init_db()
    settings = get_settings()
    worker = ScanWorker(settings)
    await worker.run_loop()


if __name__ == "__main__":
    asyncio.run(main())
