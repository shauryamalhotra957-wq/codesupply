"""CodeSupply Pydantic schemas — all API request/response models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel

# ── Scan ─────────────────────────────────────────────────────────────────────


class ScanCreate(BaseModel):
    project_name: str | None = None


class ScanStageResponse(BaseModel):
    id: str
    stage_name: str
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    message: str | None = None
    completed_count: int | None = None
    total_count: int | None = None

    model_config = {"from_attributes": True}


class ScanResponse(BaseModel):
    id: str
    status: str
    filename: str
    file_size: int
    project_name: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    error_code: str | None = None
    total_components: int = 0
    total_vulnerabilities: int = 0
    total_manifests: int = 0
    stages: list[ScanStageResponse] = []

    model_config = {"from_attributes": True}


class ScanListResponse(BaseModel):
    items: list[ScanResponse] = []
    total: int = 0


# ── Summary ──────────────────────────────────────────────────────────────────


class ScanSummaryResponse(BaseModel):
    scan_id: str
    total_components: int = 0
    total_vulnerabilities: int = 0
    total_high_critical: int = 0
    total_unknown_versions: int = 0
    components_by_ecosystem: dict[str, int] = {}
    components_by_risk: dict[str, int] = {}
    components_by_type: dict[str, int] = {}
    vulnerabilities_by_severity: dict[str, int] = {}
    sbom_valid: bool | None = None
    intelligence_status: str = "unknown"
    intelligence_checked: int = 0
    intelligence_total: int = 0
    intelligence_cached: int = 0
    scan_duration_seconds: float | None = None
    manifests_discovered: int = 0


# ── Vulnerability ────────────────────────────────────────────────────────────


class VulnerabilityResponse(BaseModel):
    id: str
    vuln_id: str
    aliases: list[str] = []
    summary: str | None = None
    severity: str = "unknown"
    affected_range: str | None = None
    fixed_version: str | None = None
    references: list[Any] = []
    source: str = "osv"
    modified_at: datetime | None = None
    cvss_score: float | None = None
    cvss_vector: str | None = None
    component_id: str = ""
    component_name: str | None = None
    component_version: str | None = None
    component_ecosystem: str | None = None

    model_config = {"from_attributes": True}


class VulnerabilityListResponse(BaseModel):
    items: list[VulnerabilityResponse] = []
    total: int = 0


# ── Risk ─────────────────────────────────────────────────────────────────────


class RiskReasonResponse(BaseModel):
    id: str
    reason_type: str
    description: str
    severity_contribution: float

    model_config = {"from_attributes": True}


# ── Evidence ─────────────────────────────────────────────────────────────────


class EvidenceResponse(BaseModel):
    id: str
    source_file: str
    source_location: str | None = None
    method: str
    confidence: str
    value: str
    evidence_type: str

    model_config = {"from_attributes": True}


# ── Component ────────────────────────────────────────────────────────────────


class ComponentResponse(BaseModel):
    id: str
    name: str
    version: str | None = None
    ecosystem: str
    package_manager: str | None = None
    dependency_type: str
    source_file: str
    source_location: str | None = None
    version_confidence: str
    purl: str | None = None
    license: str | None = None
    risk_level: str = "unknown"
    risk_score: float | None = None
    original_declaration: str | None = None
    normalized_name: str
    vulnerabilities: list[VulnerabilityResponse] = []
    risk_reasons: list[RiskReasonResponse] = []
    evidence: list[EvidenceResponse] = []

    model_config = {"from_attributes": True}


class ComponentListResponse(BaseModel):
    items: list[ComponentResponse] = []
    total: int = 0
    page: int = 1
    per_page: int = 50
    total_pages: int = 0


# ── Graph ────────────────────────────────────────────────────────────────────


class GraphNodeResponse(BaseModel):
    id: str
    name: str
    version: str | None = None
    ecosystem: str
    risk_level: str = "unknown"
    dependency_type: str
    vulnerability_count: int = 0


class GraphEdgeResponse(BaseModel):
    id: str
    source: str
    target: str
    confidence: str = "high"


class GraphResponse(BaseModel):
    nodes: list[Any] = []
    edges: list[Any] = []
    total_nodes: int = 0
    total_edges: int = 0
    truncated: bool = False


# ── SBOM ─────────────────────────────────────────────────────────────────────


class SBOMResponse(BaseModel):
    format: str = "CycloneDX"
    spec_version: str = "1.7"
    component_count: int = 0
    relationship_count: int = 0
    is_valid: bool | None = None
    validation_errors: list[str] = []
    validation_warnings: list[str] = []
    content: Any = None


# ── Dependency Edge ──────────────────────────────────────────────────────────


class DependencyEdgeResponse(BaseModel):
    id: str
    source_component_id: str
    target_component_id: str
    relationship_type: str
    confidence: str
    source_file: str
    evidence_method: str

    model_config = {"from_attributes": True}


# ── Error ────────────────────────────────────────────────────────────────────


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


# ── Health ───────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    database: str = "unknown"


# ── Progress ─────────────────────────────────────────────────────────────────


class ProgressResponse(BaseModel):
    stage: str
    completed: int
    total: int
    message: str | None = None


# ── AI Explanation ────────────────────────────────────────────────────────────


class ComponentExplanationResponse(BaseModel):
    component_id: str
    component_name: str
    version: str | None = None
    summary: str
    why_it_matters: str
    what_to_do: str
    technical_detail: str
    label: str = "AI-assisted explanation"
    disclaimer: str = (
        "Recommendations are generated from detected project metadata and available findings. "
        "Verify changes before applying them."
    )
