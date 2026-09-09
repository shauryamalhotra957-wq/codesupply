from collections.abc import Sequence
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

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
    VulnerabilityCache,
    VulnerabilityFinding,
)


class ScanRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_scan(self, scan: Scan) -> Scan:
        self.session.add(scan)
        await self.session.commit()
        await self.session.refresh(scan)
        return scan

    async def get_scan(self, scan_id: str) -> Scan | None:
        stmt = select(Scan).where(Scan.id == scan_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_scan_status(self, scan_id: str, status: str) -> Scan | None:
        stmt = update(Scan).where(Scan.id == scan_id).values(status=status)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_scan(scan_id)

    async def update_scan_error(self, scan_id: str, error_message: str, error_code: str) -> Scan | None:
        stmt = (
            update(Scan)
            .where(Scan.id == scan_id)
            .values(error_message=error_message, error_code=error_code, status="failed")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_scan(scan_id)

    async def create_stage(self, stage: ScanStage) -> ScanStage:
        self.session.add(stage)
        await self.session.commit()
        await self.session.refresh(stage)
        return stage

    async def update_stage(self, stage_id: str, **kwargs) -> None:
        stmt = update(ScanStage).where(ScanStage.id == stage_id).values(**kwargs)
        await self.session.execute(stmt)
        await self.session.commit()

    async def create_manifest(self, manifest: Manifest) -> Manifest:
        self.session.add(manifest)
        await self.session.commit()
        await self.session.refresh(manifest)
        return manifest

    async def get_manifests_for_scan(self, scan_id: str) -> Sequence[Manifest]:
        stmt = select(Manifest).where(Manifest.scan_id == scan_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_component(self, component: Component) -> Component:
        self.session.add(component)
        await self.session.commit()
        await self.session.refresh(component)
        return component

    async def create_components_bulk(self, components: list[Component]) -> None:
        self.session.add_all(components)
        await self.session.commit()

    async def get_components_for_scan(self, scan_id: str) -> Sequence[Component]:
        stmt = select(Component).where(Component.scan_id == scan_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_component(self, component_id: str) -> Component | None:
        stmt = select(Component).where(Component.id == component_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_edge(self, edge: DependencyEdge) -> DependencyEdge:
        self.session.add(edge)
        await self.session.commit()
        await self.session.refresh(edge)
        return edge

    async def create_edges_bulk(self, edges: list[DependencyEdge]) -> None:
        self.session.add_all(edges)
        await self.session.commit()

    async def get_edges_for_scan(self, scan_id: str) -> Sequence[DependencyEdge]:
        stmt = select(DependencyEdge).where(DependencyEdge.scan_id == scan_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_vulnerability(self, vuln: VulnerabilityFinding) -> VulnerabilityFinding:
        self.session.add(vuln)
        await self.session.commit()
        await self.session.refresh(vuln)
        return vuln

    async def create_vulnerabilities_bulk(self, vulns: list[VulnerabilityFinding]) -> None:
        self.session.add_all(vulns)
        await self.session.commit()

    async def get_vulnerabilities_for_scan(self, scan_id: str) -> Sequence[VulnerabilityFinding]:
        stmt = select(VulnerabilityFinding).where(VulnerabilityFinding.scan_id == scan_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_vulnerabilities_for_component(self, component_id: str) -> Sequence[VulnerabilityFinding]:
        stmt = select(VulnerabilityFinding).where(VulnerabilityFinding.component_id == component_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_risk_reason(self, reason: RiskReason) -> RiskReason:
        self.session.add(reason)
        await self.session.commit()
        await self.session.refresh(reason)
        return reason

    async def get_risk_reasons_for_component(self, component_id: str) -> Sequence[RiskReason]:
        stmt = select(RiskReason).where(RiskReason.component_id == component_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_evidence(self, evidence: Evidence) -> Evidence:
        self.session.add(evidence)
        await self.session.commit()
        await self.session.refresh(evidence)
        return evidence

    async def get_evidence_for_component(self, component_id: str) -> Sequence[Evidence]:
        stmt = select(Evidence).where(Evidence.component_id == component_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_evidence_for_edge(self, edge_id: str) -> Sequence[Evidence]:
        stmt = select(Evidence).where(Evidence.edge_id == edge_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def save_sbom_validation(self, validation: SBOMValidationResult) -> SBOMValidationResult:
        self.session.add(validation)
        await self.session.commit()
        await self.session.refresh(validation)
        return validation

    async def get_sbom_validation(self, scan_id: str) -> SBOMValidationResult | None:
        stmt = select(SBOMValidationResult).where(SBOMValidationResult.scan_id == scan_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_lookup_status(self, status: ExternalLookupStatus) -> ExternalLookupStatus:
        self.session.add(status)
        await self.session.commit()
        await self.session.refresh(status)
        return status

    async def get_lookup_statuses_for_scan(self, scan_id: str) -> Sequence[ExternalLookupStatus]:
        stmt = select(ExternalLookupStatus).where(ExternalLookupStatus.scan_id == scan_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def save_vulnerability_cache(self, cache: VulnerabilityCache) -> VulnerabilityCache:
        self.session.add(cache)
        await self.session.commit()
        await self.session.refresh(cache)
        return cache

    async def get_vulnerability_cache(self, ecosystem: str, package_name: str) -> Sequence[VulnerabilityCache]:
        stmt = select(VulnerabilityCache).where(
            VulnerabilityCache.ecosystem == ecosystem,
            VulnerabilityCache.package_name == package_name,
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_scan_summary(self, scan_id: str) -> dict[str, Any]:
        return {
            "components_by_ecosystem": {},
            "risk_distribution": {},
            "vulnerability_distribution": {},
            "dependency_type_distribution": {},
            "coverage_info": {},
            "sbom_status": "none",
            "intelligence_status": "none",
        }
