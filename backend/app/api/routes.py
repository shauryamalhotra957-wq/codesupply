"""CodeSupply API routes — all endpoints with full database integration."""

import json
import logging
import os
import shutil
import uuid
import zipfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.ws import manager
from app.core.config import Settings, get_settings
from app.core.database import get_db
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
from app.schemas.schemas import (
    ComponentListResponse,
    ComponentResponse,
    EvidenceResponse,
    GraphResponse,
    HealthResponse,
    RiskReasonResponse,
    SBOMResponse,
    ScanListResponse,
    ScanResponse,
    ScanStageResponse,
    ScanSummaryResponse,
    VulnerabilityListResponse,
    VulnerabilityResponse,
)
from app.workers.runner import ScanWorker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


# ── helpers ──────────────────────────────────────────────────────────────────


async def _get_scan_or_404(scan_id: str, db: AsyncSession) -> Scan:
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "SCAN_NOT_FOUND", "message": "Scan not found."}},
        )
    return scan


async def _get_stages(scan_id: str, db: AsyncSession) -> list[ScanStageResponse]:
    result = await db.execute(select(ScanStage).where(ScanStage.scan_id == scan_id).order_by(ScanStage.created_at))
    stages = result.scalars().all()
    return [
        ScanStageResponse(
            id=s.id,
            stage_name=s.stage_name,
            status=s.status,
            started_at=s.started_at,
            completed_at=s.completed_at,
            message=s.message,
            completed_count=s.completed_count,
            total_count=s.total_count,
        )
        for s in stages
    ]


def _scan_to_response(scan: Scan, stages: list[ScanStageResponse]) -> ScanResponse:
    return ScanResponse(
        id=scan.id,
        status=scan.status,
        filename=scan.filename,
        file_size=scan.file_size,
        project_name=scan.project_name,
        created_at=scan.created_at,
        started_at=scan.started_at,
        completed_at=scan.completed_at,
        error_message=scan.error_message,
        error_code=scan.error_code,
        total_components=scan.total_components,
        total_vulnerabilities=scan.total_vulnerabilities,
        total_manifests=scan.total_manifests,
        stages=stages,
    )


async def _build_component_response(comp: Component, db: AsyncSession) -> ComponentResponse:
    vulns_result = await db.execute(select(VulnerabilityFinding).where(VulnerabilityFinding.component_id == comp.id))
    vulns = vulns_result.scalars().all()

    reasons_result = await db.execute(select(RiskReason).where(RiskReason.component_id == comp.id))
    reasons = reasons_result.scalars().all()

    evidence_result = await db.execute(select(Evidence).where(Evidence.component_id == comp.id))
    evidences = evidence_result.scalars().all()

    return ComponentResponse(
        id=comp.id,
        name=comp.name,
        version=comp.version,
        ecosystem=comp.ecosystem,
        package_manager=comp.package_manager,
        dependency_type=comp.dependency_type,
        source_file=comp.source_file,
        source_location=comp.source_location,
        version_confidence=comp.version_confidence,
        purl=comp.purl,
        license=comp.license,
        risk_level=comp.risk_level,
        risk_score=comp.risk_score,
        original_declaration=comp.original_declaration,
        normalized_name=comp.normalized_name,
        vulnerabilities=[
            VulnerabilityResponse(
                id=v.id,
                vuln_id=v.vuln_id,
                aliases=v.aliases or [],
                summary=v.summary,
                severity=v.severity,
                affected_range=v.affected_range,
                fixed_version=v.fixed_version,
                references=v.references or [],
                source=v.source,
                modified_at=v.modified_at,
                cvss_score=v.cvss_score,
                cvss_vector=v.cvss_vector,
                component_id=v.component_id,
            )
            for v in vulns
        ],
        risk_reasons=[
            RiskReasonResponse(
                id=r.id,
                reason_type=r.reason_type,
                description=r.description,
                severity_contribution=r.severity_contribution,
            )
            for r in reasons
        ],
        evidence=[
            EvidenceResponse(
                id=e.id,
                source_file=e.source_file,
                source_location=e.source_location,
                method=e.method,
                confidence=e.confidence,
                value=e.value,
                evidence_type=e.evidence_type,
            )
            for e in evidences
        ],
    )


# ── SCAN ENDPOINTS ──────────────────────────────────────────────────────────


@router.post("/scans", status_code=201)
async def create_scan(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Upload a ZIP archive and start analysis."""
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_FILE_TYPE",
                    "message": "File must be a ZIP archive.",
                }
            },
        )

    # Read file content
    content = await file.read()
    file_size = len(content)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if file_size > max_bytes:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": f"This archive exceeds the {settings.MAX_UPLOAD_SIZE_MB} MB upload limit.",
                }
            },
        )

    scan_id = uuid.uuid4().hex

    # Save uploaded file
    upload_dir = Path(settings.TEMP_DIR) / scan_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename
    file_path.write_bytes(content)

    # Create scan record
    scan = Scan(
        id=scan_id,
        status="queued",
        filename=file.filename,
        file_size=file_size,
        project_name=Path(file.filename).stem,
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    logger.info(
        "scan_created",
        extra={"scan_id": scan_id, "archive_filename": file.filename, "size": file_size},
    )

    # Enqueue pipeline execution in background
    background_tasks.add_task(ScanWorker(settings).process_scan, scan_id)

    stages = await _get_stages(scan_id, db)
    return _scan_to_response(scan, stages)


@router.post("/scans/sample", status_code=201)
async def create_sample_scan(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Create a scan from the built-in sample project."""
    # Find sample project
    sample_dir = Path(__file__).resolve().parent.parent.parent.parent / "sample-projects" / "demo-project"
    if not sample_dir.exists():
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "SAMPLE_NOT_FOUND",
                    "message": "Sample project not found on server.",
                }
            },
        )

    scan_id = uuid.uuid4().hex
    upload_dir = Path(settings.TEMP_DIR) / scan_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    zip_path = upload_dir / "demo-project.zip"

    # Create ZIP from sample project
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(sample_dir):
            for f in files:
                full_path = Path(root) / f
                rel_path = full_path.relative_to(sample_dir)
                zf.write(full_path, arcname=str(rel_path).replace("\\", "/"))

    file_size = zip_path.stat().st_size

    # Create scan record
    scan = Scan(
        id=scan_id,
        status="queued",
        filename="demo-project.zip",
        file_size=file_size,
        project_name="demo-project",
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    logger.info(
        "sample_scan_created",
        extra={"scan_id": scan_id, "archive_filename": "demo-project.zip", "size": file_size},
    )

    # Enqueue pipeline execution in background
    background_tasks.add_task(ScanWorker(settings).process_scan, scan_id)

    stages = await _get_stages(scan_id, db)
    return _scan_to_response(scan, stages)


@router.get("/scans", response_model=ScanListResponse)
async def list_scans(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all scans ordered by creation date descending."""
    result = await db.execute(select(Scan).order_by(Scan.created_at.desc()).offset(offset).limit(limit))
    scans = result.scalars().all()

    total_result = await db.execute(select(func.count(Scan.id)))
    total = total_result.scalar() or 0

    items = []
    for scan in scans:
        stages = await _get_stages(scan.id, db)
        items.append(_scan_to_response(scan, stages))

    return ScanListResponse(items=items, total=total)


@router.get("/scans/{scan_id}")
async def get_scan(scan_id: str, db: AsyncSession = Depends(get_db)):
    """Get scan status and details."""
    scan = await _get_scan_or_404(scan_id, db)
    stages = await _get_stages(scan_id, db)
    return _scan_to_response(scan, stages)


@router.get("/scans/{scan_id}/summary")
async def get_scan_summary(scan_id: str, db: AsyncSession = Depends(get_db)):
    """Get aggregated scan summary with distributions."""
    scan = await _get_scan_or_404(scan_id, db)

    # Components by ecosystem
    eco_result = await db.execute(
        select(Component.ecosystem, func.count()).where(Component.scan_id == scan_id).group_by(Component.ecosystem)
    )
    components_by_ecosystem = dict(eco_result.all())

    # Components by risk
    risk_result = await db.execute(
        select(Component.risk_level, func.count()).where(Component.scan_id == scan_id).group_by(Component.risk_level)
    )
    components_by_risk = dict(risk_result.all())

    # Components by dependency type
    type_result = await db.execute(
        select(Component.dependency_type, func.count())
        .where(Component.scan_id == scan_id)
        .group_by(Component.dependency_type)
    )
    components_by_type = dict(type_result.all())

    # Vulnerabilities by severity
    sev_result = await db.execute(
        select(VulnerabilityFinding.severity, func.count())
        .where(VulnerabilityFinding.scan_id == scan_id)
        .group_by(VulnerabilityFinding.severity)
    )
    vulnerabilities_by_severity = dict(sev_result.all())

    # Total high/critical
    total_high_critical = sum(v for k, v in components_by_risk.items() if k in ("critical", "high"))

    # Unknown versions
    unknown_versions_result = await db.execute(
        select(func.count()).where(Component.scan_id == scan_id, Component.version.is_(None))
    )
    total_unknown_versions = unknown_versions_result.scalar() or 0

    # SBOM validation status
    sbom_val_result = await db.execute(select(SBOMValidationResult).where(SBOMValidationResult.scan_id == scan_id))
    sbom_val = sbom_val_result.scalar_one_or_none()
    sbom_valid = sbom_val.is_valid if sbom_val else None

    # Intelligence status
    lookup_result = await db.execute(select(ExternalLookupStatus).where(ExternalLookupStatus.scan_id == scan_id))
    lookups = lookup_result.scalars().all()
    intelligence_total = len(lookups)
    intelligence_checked = sum(1 for item in lookups if item.status == "checked")
    intelligence_cached = sum(1 for item in lookups if item.status == "cached")
    intelligence_unavailable = sum(1 for item in lookups if item.status == "unavailable")

    intelligence_status = "live"
    if intelligence_unavailable > 0 and intelligence_checked == 0:
        intelligence_status = "unavailable"
    elif intelligence_unavailable > 0:
        intelligence_status = "partial"
    elif intelligence_cached > 0 and intelligence_checked == 0:
        intelligence_status = "cached"

    # Scan duration
    scan_duration = None
    if scan.started_at and scan.completed_at:
        scan_duration = (scan.completed_at - scan.started_at).total_seconds()

    # Manifests
    manifest_result = await db.execute(select(func.count()).where(Manifest.scan_id == scan_id))
    manifests_discovered = manifest_result.scalar() or 0

    return ScanSummaryResponse(
        scan_id=scan_id,
        total_components=scan.total_components,
        total_vulnerabilities=scan.total_vulnerabilities,
        total_high_critical=total_high_critical,
        total_unknown_versions=total_unknown_versions,
        components_by_ecosystem=components_by_ecosystem,
        components_by_risk=components_by_risk,
        components_by_type=components_by_type,
        vulnerabilities_by_severity=vulnerabilities_by_severity,
        sbom_valid=sbom_valid,
        intelligence_status=intelligence_status,
        intelligence_checked=intelligence_checked,
        intelligence_total=intelligence_total,
        intelligence_cached=intelligence_cached,
        scan_duration_seconds=scan_duration,
        manifests_discovered=manifests_discovered,
    )


@router.get("/scans/{scan_id}/components")
async def get_scan_components(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    search: str | None = Query(None),
    ecosystem: str | None = Query(None),
    risk_level: str | None = Query(None),
    dependency_type: str | None = Query(None),
    version_confidence: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    sort_by: str = Query("name"),
    sort_order: str = Query("asc"),
):
    """Get components with filtering, searching, and pagination."""
    await _get_scan_or_404(scan_id, db)

    query = select(Component).where(Component.scan_id == scan_id)

    if search:
        query = query.where(Component.name.ilike(f"%{search}%"))
    if ecosystem:
        query = query.where(Component.ecosystem == ecosystem)
    if risk_level:
        query = query.where(Component.risk_level == risk_level)
    if dependency_type:
        query = query.where(Component.dependency_type == dependency_type)
    if version_confidence:
        query = query.where(Component.version_confidence == version_confidence)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Sort
    sort_col = getattr(Component, sort_by, Component.name)
    if sort_order == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    # Paginate
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    result = await db.execute(query)
    components = result.scalars().all()

    items = []
    for comp in components:
        items.append(await _build_component_response(comp, db))

    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

    return ComponentListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/scans/{scan_id}/components/{component_id}")
async def get_scan_component(
    scan_id: str,
    component_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed component information."""
    await _get_scan_or_404(scan_id, db)

    result = await db.execute(select(Component).where(Component.id == component_id, Component.scan_id == scan_id))
    comp = result.scalar_one_or_none()
    if not comp:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "COMPONENT_NOT_FOUND",
                    "message": "Component not found.",
                }
            },
        )

    return await _build_component_response(comp, db)


@router.get("/scans/{scan_id}/graph")
async def get_scan_graph(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    max_nodes: int = Query(250, ge=1, le=5000),
    highlight_component_id: str | None = Query(None),
):
    """Get dependency graph data for visualization."""
    await _get_scan_or_404(scan_id, db)

    # Get total counts
    total_nodes_result = await db.execute(select(func.count()).where(Component.scan_id == scan_id))
    total_nodes = total_nodes_result.scalar() or 0

    total_edges_result = await db.execute(select(func.count()).where(DependencyEdge.scan_id == scan_id))
    total_edges = total_edges_result.scalar() or 0

    truncated = total_nodes > max_nodes

    # Get components (limited)
    comp_query = select(Component).where(Component.scan_id == scan_id).limit(max_nodes)
    comp_result = await db.execute(comp_query)
    components = comp_result.scalars().all()
    comp_ids = {c.id for c in components}

    # Get vulnerability counts per component
    vuln_counts: dict[str, int] = {}
    if comp_ids:
        vuln_result = await db.execute(
            select(VulnerabilityFinding.component_id, func.count())
            .where(VulnerabilityFinding.scan_id == scan_id)
            .group_by(VulnerabilityFinding.component_id)
        )
        vuln_counts = dict(vuln_result.all())

    nodes = []
    for c in components:
        nodes.append(
            {
                "id": c.id,
                "name": c.name,
                "version": c.version,
                "ecosystem": c.ecosystem,
                "risk_level": c.risk_level,
                "dependency_type": c.dependency_type,
                "vulnerability_count": vuln_counts.get(c.id, 0),
            }
        )

    # Get edges between included components
    edge_query = select(DependencyEdge).where(DependencyEdge.scan_id == scan_id)
    edge_result = await db.execute(edge_query)
    edges_raw = edge_result.scalars().all()

    edges = []
    for e in edges_raw:
        if e.source_component_id in comp_ids and e.target_component_id in comp_ids:
            edges.append(
                {
                    "id": e.id,
                    "source": e.source_component_id,
                    "target": e.target_component_id,
                    "confidence": e.confidence,
                }
            )

    return GraphResponse(
        nodes=nodes,
        edges=edges,
        total_nodes=total_nodes,
        total_edges=total_edges,
        truncated=truncated,
    )


@router.get("/scans/{scan_id}/vulnerabilities")
async def get_scan_vulnerabilities(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all vulnerabilities found in a scan."""
    await _get_scan_or_404(scan_id, db)

    result = await db.execute(select(VulnerabilityFinding).where(VulnerabilityFinding.scan_id == scan_id))
    vulns = result.scalars().all()

    # Enrich with component info
    items = []
    for v in vulns:
        comp_result = await db.execute(select(Component).where(Component.id == v.component_id))
        comp = comp_result.scalar_one_or_none()

        items.append(
            VulnerabilityResponse(
                id=v.id,
                vuln_id=v.vuln_id,
                aliases=v.aliases or [],
                summary=v.summary,
                severity=v.severity,
                affected_range=v.affected_range,
                fixed_version=v.fixed_version,
                references=v.references or [],
                source=v.source,
                modified_at=v.modified_at,
                cvss_score=v.cvss_score,
                cvss_vector=v.cvss_vector,
                component_id=v.component_id,
                component_name=comp.name if comp else None,
                component_version=comp.version if comp else None,
                component_ecosystem=comp.ecosystem if comp else None,
            )
        )

    return VulnerabilityListResponse(items=items, total=len(items))


@router.get("/scans/{scan_id}/sbom")
async def get_scan_sbom(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get SBOM metadata and content."""
    scan = await _get_scan_or_404(scan_id, db)

    if scan.status != "complete":
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "SCAN_INCOMPLETE",
                    "message": "Scan must be complete before accessing SBOM.",
                }
            },
        )

    # Get SBOM from scan's stored data
    from app.sbom.generator import CycloneDXGenerator

    comp_result = await db.execute(select(Component).where(Component.scan_id == scan_id))
    components = comp_result.scalars().all()

    edge_result = await db.execute(select(DependencyEdge).where(DependencyEdge.scan_id == scan_id))
    edges = edge_result.scalars().all()

    generator = CycloneDXGenerator()
    sbom_dict = generator.generate(scan, list(components), list(edges))

    # Get validation result
    val_result = await db.execute(select(SBOMValidationResult).where(SBOMValidationResult.scan_id == scan_id))
    validation = val_result.scalar_one_or_none()

    return SBOMResponse(
        format="CycloneDX",
        spec_version="1.7",
        component_count=len(components),
        relationship_count=len(edges),
        is_valid=validation.is_valid if validation else None,
        validation_errors=validation.errors if validation else [],
        validation_warnings=validation.warnings if validation else [],
        content=sbom_dict,
    )


@router.get("/scans/{scan_id}/download/sbom")
async def download_scan_sbom(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Download SBOM as a JSON file."""
    scan = await _get_scan_or_404(scan_id, db)

    if scan.status != "complete":
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "SCAN_INCOMPLETE",
                    "message": "Scan must be complete before downloading SBOM.",
                }
            },
        )

    from app.sbom.generator import CycloneDXGenerator

    comp_result = await db.execute(select(Component).where(Component.scan_id == scan_id))
    components = comp_result.scalars().all()

    edge_result = await db.execute(select(DependencyEdge).where(DependencyEdge.scan_id == scan_id))
    edges = edge_result.scalars().all()

    generator = CycloneDXGenerator()
    sbom_dict = generator.generate(scan, list(components), list(edges))
    sbom_json = json.dumps(sbom_dict, indent=2, default=str)

    filename = f"codesupply-sbom-{scan.project_name or scan_id}.cdx.json"

    return StreamingResponse(
        iter([sbom_json.encode()]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/scans/{scan_id}/evidence/{evidence_id}")
async def get_evidence(
    scan_id: str,
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific evidence record."""
    await _get_scan_or_404(scan_id, db)

    result = await db.execute(select(Evidence).where(Evidence.id == evidence_id, Evidence.scan_id == scan_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "EVIDENCE_NOT_FOUND",
                    "message": "Evidence record not found.",
                }
            },
        )

    return EvidenceResponse(
        id=evidence.id,
        source_file=evidence.source_file,
        source_location=evidence.source_location,
        method=evidence.method,
        confidence=evidence.confidence,
        value=evidence.value,
        evidence_type=evidence.evidence_type,
    )


@router.post("/scans/{scan_id}/retry", status_code=201)
async def retry_scan(
    scan_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Retry a failed scan."""
    scan_result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = scan_result.scalar_one_or_none()
    if not scan:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "SCAN_NOT_FOUND", "message": f"Scan '{scan_id}' does not exist."}},
        )

    if scan.status not in ("failed", "complete"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "SCAN_IN_PROGRESS",
                    "message": "Scan is still in progress.",
                }
            },
        )

    # Create new scan pointing to the same uploaded file
    new_scan_id = uuid.uuid4().hex
    old_dir = Path(settings.TEMP_DIR) / scan_id
    new_dir = Path(settings.TEMP_DIR) / new_scan_id

    if old_dir.exists():
        shutil.copytree(old_dir, new_dir)
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "ARCHIVE_EXPIRED",
                    "message": "Original archive has been cleaned up. Please upload again.",
                }
            },
        )

    new_scan = Scan(
        id=new_scan_id,
        status="queued",
        filename=scan.filename,
        file_size=scan.file_size,
        project_name=scan.project_name,
    )
    db.add(new_scan)
    await db.commit()
    await db.refresh(new_scan)

    # Enqueue pipeline execution in background
    background_tasks.add_task(ScanWorker(settings).process_scan, new_scan_id)

    stages = await _get_stages(new_scan_id, db)
    return _scan_to_response(new_scan, stages)


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    """Health check endpoint."""
    try:
        await db.execute(select(func.count()).select_from(Scan))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        version="1.0.0",
        database=db_status,
    )


@router.websocket("/scans/{scan_id}/ws")
async def websocket_scan_endpoint(websocket: WebSocket, scan_id: str):
    await manager.connect(websocket, scan_id)
    try:
        while True:
            # We don't really expect client to send anything, but keep connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, scan_id)


@router.get("/scans/{scan_id}/diff/{other_scan_id}")
async def get_scan_diff(
    scan_id: str,
    other_scan_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Compare two scans and return differences in dependencies and vulnerabilities."""
    scan1 = await _get_scan_or_404(scan_id, db)
    scan2 = await _get_scan_or_404(other_scan_id, db)

    # Get components
    c1_res = await db.execute(select(Component).where(Component.scan_id == scan_id))
    c2_res = await db.execute(select(Component).where(Component.scan_id == other_scan_id))

    c1 = {f"{c.ecosystem}:{c.name}": c for c in c1_res.scalars().all()}
    c2 = {f"{c.ecosystem}:{c.name}": c for c in c2_res.scalars().all()}

    added_components = []
    removed_components = []
    version_changes = []

    for key, comp2 in c2.items():
        if key not in c1:
            added_components.append(
                {"ecosystem": comp2.ecosystem, "name": comp2.name, "version": comp2.version, "purl": comp2.purl}
            )
        else:
            comp1 = c1[key]
            if comp1.version != comp2.version:
                version_changes.append(
                    {
                        "ecosystem": comp2.ecosystem,
                        "name": comp2.name,
                        "old_version": comp1.version,
                        "new_version": comp2.version,
                        "purl": comp2.purl,
                    }
                )

    for key, comp1 in c1.items():
        if key not in c2:
            removed_components.append(
                {"ecosystem": comp1.ecosystem, "name": comp1.name, "version": comp1.version, "purl": comp1.purl}
            )

    # Get vulnerabilities
    v1_res = await db.execute(select(VulnerabilityFinding).where(VulnerabilityFinding.scan_id == scan_id))
    v2_res = await db.execute(select(VulnerabilityFinding).where(VulnerabilityFinding.scan_id == other_scan_id))

    v1 = {f"{v.component_id}:{v.vuln_id}": v for v in v1_res.scalars().all()}
    v2 = {f"{v.component_id}:{v.vuln_id}": v for v in v2_res.scalars().all()}

    added_vulns = []
    resolved_vulns = []

    for key, vuln2 in v2.items():
        if key not in v1:
            added_vulns.append(
                {
                    "vuln_id": vuln2.vuln_id,
                    "severity": vuln2.severity,
                    "summary": vuln2.summary,
                }
            )

    for key, vuln1 in v1.items():
        if key not in v2:
            resolved_vulns.append(
                {
                    "vuln_id": vuln1.vuln_id,
                    "severity": vuln1.severity,
                    "summary": vuln1.summary,
                }
            )

    return {
        "base_scan": {"id": scan1.id, "created_at": scan1.created_at},
        "compare_scan": {"id": scan2.id, "created_at": scan2.created_at},
        "components": {"added": added_components, "removed": removed_components, "version_changed": version_changes},
        "vulnerabilities": {"added": added_vulns, "resolved": resolved_vulns},
    }
