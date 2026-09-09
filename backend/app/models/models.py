import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def generate_uuid() -> str:
    return uuid.uuid4().hex


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    status: Mapped[str] = mapped_column(String, index=True)
    filename: Mapped[str] = mapped_column(String)
    file_size: Mapped[int] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
    error_code: Mapped[str | None] = mapped_column(String)

    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    total_components: Mapped[int] = mapped_column(Integer, default=0)
    total_vulnerabilities: Mapped[int] = mapped_column(Integer, default=0)
    total_manifests: Mapped[int] = mapped_column(Integer, default=0)

    project_name: Mapped[str | None] = mapped_column(String)


class ScanStage(Base):
    __tablename__ = "scan_stages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.id"), index=True)
    stage_name: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)

    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    message: Mapped[str | None] = mapped_column(Text)

    completed_count: Mapped[int | None] = mapped_column(Integer)
    total_count: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class Manifest(Base):
    __tablename__ = "manifests"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.id"), index=True)
    file_path: Mapped[str] = mapped_column(String)
    ecosystem: Mapped[str] = mapped_column(String)
    manifest_type: Mapped[str] = mapped_column(String)

    is_parseable: Mapped[bool] = mapped_column(default=True)
    file_size: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class Component(Base):
    __tablename__ = "components"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.id"), index=True)
    manifest_id: Mapped[str | None] = mapped_column(ForeignKey("manifests.id"))

    name: Mapped[str] = mapped_column(String, index=True)
    version: Mapped[str | None] = mapped_column(String)
    ecosystem: Mapped[str] = mapped_column(String)
    package_manager: Mapped[str | None] = mapped_column(String)

    dependency_type: Mapped[str] = mapped_column(String)
    parent_component_id: Mapped[str | None] = mapped_column(ForeignKey("components.id"))

    source_file: Mapped[str] = mapped_column(String)
    source_location: Mapped[str | None] = mapped_column(String)

    version_confidence: Mapped[str] = mapped_column(String)
    purl: Mapped[str | None] = mapped_column(String)
    license: Mapped[str | None] = mapped_column(String)

    risk_level: Mapped[str] = mapped_column(String, default="unknown")
    risk_score: Mapped[float | None] = mapped_column(Float)

    original_declaration: Mapped[str | None] = mapped_column(String)
    normalized_name: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class DependencyEdge(Base):
    __tablename__ = "dependency_edges"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.id"), index=True)
    source_component_id: Mapped[str] = mapped_column(ForeignKey("components.id"))
    target_component_id: Mapped[str] = mapped_column(ForeignKey("components.id"))

    relationship_type: Mapped[str] = mapped_column(String)
    confidence: Mapped[str] = mapped_column(String)
    source_file: Mapped[str] = mapped_column(String)
    evidence_method: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class VulnerabilityFinding(Base):
    __tablename__ = "vulnerability_findings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.id"), index=True)
    component_id: Mapped[str] = mapped_column(ForeignKey("components.id"), index=True)

    vuln_id: Mapped[str] = mapped_column(String)
    aliases: Mapped[list[Any]] = mapped_column(JSON, default=list)

    summary: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String)

    affected_range: Mapped[str | None] = mapped_column(String)
    fixed_version: Mapped[str | None] = mapped_column(String)

    references: Mapped[list[Any]] = mapped_column(JSON, default=list)
    source: Mapped[str] = mapped_column(String)
    modified_at: Mapped[datetime | None] = mapped_column(DateTime)

    cvss_score: Mapped[float | None] = mapped_column(Float)
    cvss_vector: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class RiskReason(Base):
    __tablename__ = "risk_reasons"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.id"), index=True)
    component_id: Mapped[str] = mapped_column(ForeignKey("components.id"), index=True)

    reason_type: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    severity_contribution: Mapped[float] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class Evidence(Base):
    __tablename__ = "evidences"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.id"), index=True)
    component_id: Mapped[str | None] = mapped_column(ForeignKey("components.id"))
    edge_id: Mapped[str | None] = mapped_column(ForeignKey("dependency_edges.id"))

    source_file: Mapped[str] = mapped_column(String)
    source_location: Mapped[str | None] = mapped_column(String)

    method: Mapped[str] = mapped_column(String)
    confidence: Mapped[str] = mapped_column(String)

    value: Mapped[str] = mapped_column(String)
    evidence_type: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class ExternalLookupStatus(Base):
    __tablename__ = "external_lookup_statuses"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.id"), index=True)
    component_id: Mapped[str | None] = mapped_column(ForeignKey("components.id"))

    service: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)

    checked_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    cached_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_message: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class SBOMValidationResult(Base):
    __tablename__ = "sbom_validation_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.id"), index=True)

    is_valid: Mapped[bool] = mapped_column(default=False)
    format: Mapped[str] = mapped_column(String)
    spec_version: Mapped[str] = mapped_column(String)

    errors: Mapped[list[Any]] = mapped_column(JSON, default=list)
    warnings: Mapped[list[Any]] = mapped_column(JSON, default=list)

    validated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class VulnerabilityCache(Base):
    __tablename__ = "vulnerability_cache"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)

    ecosystem: Mapped[str] = mapped_column(String)
    package_name: Mapped[str] = mapped_column(String)
    package_version: Mapped[str | None] = mapped_column(String)
    purl: Mapped[str | None] = mapped_column(String)

    response_data: Mapped[dict] = mapped_column(JSON)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    source: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
