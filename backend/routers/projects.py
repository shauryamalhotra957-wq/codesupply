import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, File, HTTPException, Response, UploadFile
from fastapi.responses import JSONResponse

from backend.database import DatabaseRepository
from backend.models import (
    ComponentModel,
    FindingModel,
    ProjectModel,
    SbomComparisonModel,
    VulnerabilityModel,
)
from backend.services.report_generator import ReportGenerator
from backend.services.scanner_service import ScannerService
from scanner.normalization.normalizer import NormalizedComponent
from scanner.sbom.differ import SbomDiffer
from scanner.sbom.spdx_generator import SPDXGenerator
from scanner.security.safe_extractor import SafeExtractionError
from scanner.security.vuln_engine import VulnerabilityEngine

router = APIRouter(prefix="/api/projects", tags=["projects"])
scanner_service = ScannerService()


@router.get("", response_model=List[ProjectModel])
def list_projects():
    """Lists all scanned projects."""
    return DatabaseRepository.get_projects()


@router.post("/upload", response_model=ProjectModel)
async def upload_project(file: UploadFile = File(...)):
    """
    Accepts a project ZIP archive, performs safe validation, static parsing,
    risk evaluation, and stores normalized SBOM records.
    """
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .zip archives are supported.")

    temp_zip = None
    try:
        # Write uploaded bytes to a safe temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            temp_zip = Path(tmp.name)
            contents = await file.read()
            tmp.write(contents)
            file_size = len(contents)

        project_name = Path(file.filename).stem or "Uploaded_Project"

        result = scanner_service.scan_archive(
            zip_path=temp_zip,
            project_name=project_name,
            file_size_bytes=file_size,
        )
        return result

    except SafeExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process archive: {str(e)}")
    finally:
        if temp_zip and temp_zip.exists():
            try:
                temp_zip.unlink()
            except Exception:
                pass


@router.post("/demo/{sample_type}", response_model=ProjectModel)
def load_sample_project(sample_type: str):
    """
    Loads a built-in sample project for instant demonstration.
    Available types: 'python-project', 'node-project', 'mixed-project', 'broken-project'
    """
    samples_dir = Path(__file__).resolve().parent.parent.parent / "samples"
    target_sample = samples_dir / sample_type

    if not target_sample.exists() or not target_sample.is_dir():
        # Fallback names
        alt_map = {
            "python": "python-project",
            "node": "node-project",
            "mixed": "mixed-project",
            "broken": "broken-project",
        }
        if sample_type in alt_map:
            target_sample = samples_dir / alt_map[sample_type]

    if not target_sample.exists():
        raise HTTPException(status_code=404, detail=f"Sample project '{sample_type}' not found.")

    display_name = target_sample.name.replace("-", " ").title()
    result = scanner_service.scan_directory(
        workspace_dir=target_sample,
        project_name=display_name,
    )
    return result


@router.get("/{project_id}", response_model=ProjectModel)
def get_project(project_id: str):
    """Retrieves metadata and summary metrics for a scanned project."""
    proj = DatabaseRepository.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found.")
    return proj


@router.get("/{project_id}/components", response_model=List[ComponentModel])
def get_project_components(project_id: str):
    """Retrieves all normalized components and dependencies for a project."""
    proj = DatabaseRepository.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found.")
    return DatabaseRepository.get_components(project_id)


@router.get("/{project_id}/graph")
def get_project_graph(project_id: str):
    """Retrieves the React Flow DAG node/edge representation of dependencies."""
    graph = DatabaseRepository.get_graph(project_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Dependency graph not found.")
    return graph


@router.get("/{project_id}/findings", response_model=List[FindingModel])
def get_project_findings(project_id: str):
    """Retrieves supply-chain and hygiene risk findings with explanations and recommendations."""
    return DatabaseRepository.get_findings(project_id)


@router.get("/{project_id}/sbom")
def get_project_sbom(project_id: str):
    """Retrieves the full CycloneDX v1.5 JSON SBOM document."""
    sbom = DatabaseRepository.get_sbom(project_id)
    if not sbom:
        raise HTTPException(status_code=404, detail="SBOM not found for project.")
    return JSONResponse(content=sbom)


@router.get("/{project_id}/spdx")
def get_project_spdx(project_id: str):
    """Retrieves the full SPDX v2.3 JSON SBOM document."""
    proj = DatabaseRepository.get_project(project_id)
    raw_components = DatabaseRepository.get_components(project_id)
    if not proj or not raw_components:
        raise HTTPException(status_code=404, detail="Project or components not found.")

    components = [
        NormalizedComponent(
            name=c.get("name", ""),
            version=c.get("version"),
            raw_specifier=c.get("raw_specifier"),
            ecosystem=c.get("ecosystem", "generic"),
            direct=c.get("direct", True),
            source_file=c.get("source_file", ""),
            purl=c.get("purl", ""),
            scope=c.get("scope", "required"),
            license=c.get("license"),
            integrity=c.get("integrity"),
            resolved_url=c.get("resolved_url"),
        )
        for c in raw_components
    ]
    spdx_doc = SPDXGenerator.generate_sbom(project_name=proj["name"], components=components)
    return JSONResponse(content=spdx_doc)


@router.get("/{project_id}/export/cyclonedx")
def export_cyclonedx_file(project_id: str):
    """Downloads the CycloneDX v1.5 JSON file."""
    proj = DatabaseRepository.get_project(project_id)
    sbom = DatabaseRepository.get_sbom(project_id)
    if not proj or not sbom:
        raise HTTPException(status_code=404, detail="Project or SBOM not found.")

    filename = f"{proj['name'].replace(' ', '_').lower()}-cyclonedx-sbom.json"
    return Response(
        content=json.dumps(sbom, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{project_id}/export/spdx")
def export_spdx_file(project_id: str):
    """Downloads the SPDX v2.3 JSON file."""
    proj = DatabaseRepository.get_project(project_id)
    raw_components = DatabaseRepository.get_components(project_id)
    if not proj or not raw_components:
        raise HTTPException(status_code=404, detail="Project or components not found.")

    components = [
        NormalizedComponent(
            name=c.get("name", ""),
            version=c.get("version"),
            raw_specifier=c.get("raw_specifier"),
            ecosystem=c.get("ecosystem", "generic"),
            direct=c.get("direct", True),
            source_file=c.get("source_file", ""),
            purl=c.get("purl", ""),
            scope=c.get("scope", "required"),
            license=c.get("license"),
            integrity=c.get("integrity"),
            resolved_url=c.get("resolved_url"),
        )
        for c in raw_components
    ]
    spdx_doc = SPDXGenerator.generate_sbom(project_name=proj["name"], components=components)
    filename = f"{proj['name'].replace(' ', '_').lower()}-spdx-2.3-sbom.json"
    return Response(
        content=json.dumps(spdx_doc, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{project_id}/export/csv")
def export_csv(project_id: str):
    """Exports components list as a CSV file."""
    proj = DatabaseRepository.get_project(project_id)
    components = DatabaseRepository.get_components(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found.")

    csv_data = ReportGenerator.generate_csv(components)
    filename = f"{proj['name'].replace(' ', '_').lower()}-components.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{project_id}/report")
def export_pdf_report(project_id: str):
    """Generates and downloads a complete PDF audit report."""
    proj = DatabaseRepository.get_project(project_id)
    components = DatabaseRepository.get_components(project_id)
    findings = DatabaseRepository.get_findings(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found.")

    pdf_bytes = ReportGenerator.generate_pdf(proj, components, findings)
    filename = f"{proj['name'].replace(' ', '_').lower()}-audit-report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{project_id}/vulnerabilities", response_model=List[VulnerabilityModel])
def get_project_vulnerabilities(project_id: str):
    """Retrieves all matched CVE vulnerability and exploitation records for the project."""
    components = DatabaseRepository.get_components(project_id)
    if components is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    vulnerabilities = []
    for c in components:
        matches = VulnerabilityEngine.match_component(
            c.get("name", ""), c.get("version"), c.get("ecosystem", "")
        )
        for m in matches:
            vulnerabilities.append(VulnerabilityModel(**m))

    return vulnerabilities


@router.get("/{base_project_id}/compare/{target_project_id}", response_model=SbomComparisonModel)
def compare_sbom_projects(base_project_id: str, target_project_id: str):
    """Calculates full SBOM diff, version migrations, and vulnerability drift between two projects."""
    base_proj = DatabaseRepository.get_project(base_project_id)
    target_proj = DatabaseRepository.get_project(target_project_id)
    if not base_proj or not target_proj:
        raise HTTPException(status_code=404, detail="One or both projects not found.")

    base_components = DatabaseRepository.get_components(base_project_id)
    target_components = DatabaseRepository.get_components(target_project_id)

    diff_result = SbomDiffer.compare_projects(
        base_project_id=base_project_id,
        target_project_id=target_project_id,
        base_components=base_components,
        target_components=target_components,
    )
    return diff_result

