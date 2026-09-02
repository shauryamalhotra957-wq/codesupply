from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ManifestFileItem(BaseModel):
    file_name: str
    relative_path: str
    full_path: Optional[str] = None
    ecosystem: str


class ComponentModel(BaseModel):
    name: str
    version: Optional[str] = None
    raw_specifier: Optional[str] = None
    ecosystem: str
    direct: bool = True
    source_file: str = ""
    source_files: List[str] = Field(default_factory=list)
    purl: str
    scope: str = "required"
    license: Optional[str] = None
    integrity: Optional[str] = None
    resolved_url: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FindingModel(BaseModel):
    component_name: str
    severity: str
    category: str
    title: str
    evidence: Optional[str] = ""
    explanation: Optional[str] = ""
    recommendation: Optional[str] = ""


class ProjectModel(BaseModel):
    id: str
    name: str
    created_at: str
    file_size_bytes: int = 0
    ecosystems: List[str] = Field(default_factory=list)
    manifest_files: List[ManifestFileItem] = Field(default_factory=list)
    total_components: int = 0
    direct_count: int = 0
    transitive_count: int = 0
    pinned_count: int = 0
    unpinned_count: int = 0
    findings_count: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    medium_findings: int = 0
    low_findings: int = 0
    status: str = "READY"


class GraphDataModel(BaseModel):
    root_id: str
    total_nodes: int
    total_edges: int
    react_flow: Dict[str, Any]
    cyclonedx_dependencies: List[Dict[str, Any]]
