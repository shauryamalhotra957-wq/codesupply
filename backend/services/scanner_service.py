import datetime
import uuid
from pathlib import Path
from typing import Any, Dict, List

from backend.database import DatabaseRepository
from backend.services.risk_engine import RiskEngine
from backend.services.risk_explanation_service import RiskExplanationService
from scanner.detection.detector import ProjectDetector
from scanner.normalization.normalizer import DependencyNormalizer, NormalizedComponent
from scanner.parsers.base import ParsedDependency
from scanner.parsers.cargo_parser import CargoParser
from scanner.parsers.golang_parser import GolangParser
from scanner.parsers.node_parser import NodeParser
from scanner.parsers.python_parser import PythonParser
from scanner.relationships.graph_builder import DependencyGraphBuilder
from scanner.sbom.cyclonedx_generator import CycloneDXGenerator
from scanner.security.safe_extractor import SafeExtractor


class ScannerService:
    """
    Coordinates the end-to-end scanning pipeline:
    Extract -> Detect -> Parse -> Normalize -> Analyze Risks -> Build Graph -> Generate CycloneDX & SPDX -> Persist.
    """

    def __init__(self):
        self.python_parser = PythonParser()
        self.node_parser = NodeParser()
        self.cargo_parser = CargoParser()
        self.golang_parser = GolangParser()
        self.explanation_service = RiskExplanationService()

    def scan_archive(self, zip_path: Path | str, project_name: str, file_size_bytes: int = 0) -> Dict[str, Any]:
        project_id = f"proj_{uuid.uuid4().hex[:12]}"
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        with SafeExtractor.safe_temp_workspace(zip_path) as workspace_dir:
            return self.scan_directory(
                workspace_dir=workspace_dir,
                project_name=project_name,
                project_id=project_id,
                created_at=created_at,
                file_size_bytes=file_size_bytes,
            )

    def scan_directory(
        self,
        workspace_dir: Path,
        project_name: str,
        project_id: str = None,
        created_at: str = None,
        file_size_bytes: int = 0,
    ) -> Dict[str, Any]:
        if not project_id:
            project_id = f"proj_{uuid.uuid4().hex[:12]}"
        if not created_at:
            created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # 1. Detect project manifests and ecosystems
        detection = ProjectDetector.detect(workspace_dir)

        # 2. Parse all detected manifest files
        raw_dependencies: List[ParsedDependency] = []

        for manifest in detection.manifest_files:
            file_path = Path(manifest["full_path"])
            rel_path = manifest["relative_path"]
            filename = manifest["file_name"]

            if self.python_parser.can_parse(filename):
                parsed = self.python_parser.parse(file_path, rel_path)
                raw_dependencies.extend(parsed)
            elif self.node_parser.can_parse(filename):
                parsed = self.node_parser.parse(file_path, rel_path)
                raw_dependencies.extend(parsed)
            elif self.cargo_parser.can_parse(filename):
                parsed = self.cargo_parser.parse(file_path, rel_path)
                raw_dependencies.extend(parsed)
            elif self.golang_parser.can_parse(filename):
                parsed = self.golang_parser.parse(file_path, rel_path)
                raw_dependencies.extend(parsed)

        # 3. Normalize dependencies & PURLs
        normalized_components: List[NormalizedComponent] = DependencyNormalizer.normalize_list(raw_dependencies)

        # 4. Risk / Anomaly Analysis & Explanations
        raw_findings = RiskEngine.analyze(raw_dependencies, normalized_components)
        enriched_findings = self.explanation_service.enrich_findings(raw_findings)

        # Map findings per component name
        findings_map: Dict[str, int] = {}
        for f in enriched_findings:
            findings_map[f.component_name.lower()] = findings_map.get(f.component_name.lower(), 0) + 1

        # 5. Build Dependency Graph & DAG
        graph_data = DependencyGraphBuilder.build_graph(
            project_name=project_name,
            components=normalized_components,
            findings_map=findings_map,
        )

        # 6. Generate CycloneDX 1.5 JSON SBOM
        cyclonedx_sbom = CycloneDXGenerator.generate_sbom(
            project_name=project_name,
            components=normalized_components,
            cyclonedx_dependencies=graph_data["cyclonedx_dependencies"],
        )

        # 7. Compute Summary Metrics
        direct_count = sum(1 for c in normalized_components if c.direct)
        transitive_count = sum(1 for c in normalized_components if not c.direct)
        pinned_count = sum(
            1 for c in normalized_components if c.version and c.version not in ("unspecified", "unpinned", "")
        )
        unpinned_count = len(normalized_components) - pinned_count

        critical_f = sum(1 for f in enriched_findings if f.severity == "CRITICAL")
        high_f = sum(1 for f in enriched_findings if f.severity == "HIGH")
        medium_f = sum(1 for f in enriched_findings if f.severity == "MEDIUM")
        low_f = sum(1 for f in enriched_findings if f.severity in ("LOW", "INFO"))

        project_record = {
            "id": project_id,
            "name": project_name,
            "created_at": created_at,
            "file_size_bytes": file_size_bytes,
            "ecosystems": detection.ecosystems,
            "manifest_files": detection.manifest_files,
            "total_components": len(normalized_components),
            "direct_count": direct_count,
            "transitive_count": transitive_count,
            "pinned_count": pinned_count,
            "unpinned_count": unpinned_count,
            "findings_count": len(enriched_findings),
            "critical_findings": critical_f,
            "high_findings": high_f,
            "medium_findings": medium_f,
            "low_findings": low_f,
            "status": "READY",
        }

        # 8. Persist to Database
        DatabaseRepository.save_project(project_record)
        DatabaseRepository.save_components(project_id, [c.to_dict() for c in normalized_components])
        DatabaseRepository.save_findings(project_id, [f.to_dict() for f in enriched_findings])
        DatabaseRepository.save_sbom_and_graph(project_id, cyclonedx_sbom, graph_data, created_at)

        return project_record
