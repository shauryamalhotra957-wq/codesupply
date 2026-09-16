import logging
from datetime import timedelta

import httpx

from app.core.config import Settings
from app.models.models import Component, VulnerabilityFinding

logger = logging.getLogger(__name__)


class OSVClient:
    """Client for OSV.dev vulnerability database."""

    def __init__(self, settings: Settings):
        self.api_url = settings.OSV_API_URL
        self.batch_size = settings.OSV_BATCH_SIZE
        self.cache_ttl = timedelta(hours=settings.OSV_CACHE_TTL_HOURS)

    def _map_ecosystem(self, ecosystem: str) -> str:
        mapping = {"npm": "npm", "pypi": "PyPI", "maven": "Maven"}
        return mapping.get(ecosystem.lower(), ecosystem)

    async def query_batch(self, queries: list[dict], session: httpx.AsyncClient) -> list[dict]:
        """Query OSV with batch endpoint POST /v1/querybatch."""
        results = []
        for i in range(0, len(queries), self.batch_size):
            batch = queries[i : i + self.batch_size]
            try:
                response = await session.post(f"{self.api_url}/v1/querybatch", json={"queries": batch})
                response.raise_for_status()
                data = response.json()
                results.extend(data.get("results", []))
            except Exception as e:
                logger.error(f"Failed to query OSV batch: {e}")
                results.extend([{} for _ in batch])
        return results

    async def get_vulnerability(self, vuln_id: str) -> dict | None:
        """GET /v1/vulns/{id} for full advisory details."""
        try:
            async with httpx.AsyncClient() as session:
                response = await session.get(f"{self.api_url}/v1/vulns/{vuln_id}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch vulnerability details for {vuln_id}: {e}")
            return None

    async def check_components(
        self,
        components: list[Component],
        session: httpx.AsyncClient,
        scan_id: str,
        db_session,
    ) -> list:
        """Check a list of components against OSV."""
        queries = []
        component_map = []
        findings = []

        from app.vulnerabilities.cache import VulnerabilityCache

        cache = VulnerabilityCache()

        for component in components:
            if not component.version:
                component.lookup_status = "not_applicable"
                continue

            ecosystem = self._map_ecosystem(component.ecosystem)
            cached = await cache.get(ecosystem, component.name, component.version, db_session)
            if cached is not None:
                component.lookup_status = "completed"
                for vuln in cached.get("vulns", []):
                    findings.append(self._parse_finding(component, vuln, scan_id))
                continue

            query = {
                "package": {"name": component.name, "ecosystem": ecosystem},
                "version": component.version,
            }
            if component.purl:
                query = {"package": {"purl": component.purl}}
            queries.append(query)
            component_map.append(component)

        if queries:
            results = await self.query_batch(queries, session)
            for component, result in zip(component_map, results):
                if result == {}:
                    component.lookup_status = "unavailable"
                    continue

                component.lookup_status = "completed"
                ecosystem = self._map_ecosystem(component.ecosystem)
                await cache.set(ecosystem, component.name, component.version, result, db_session)

                for vuln in result.get("vulns", []):
                    findings.append(self._parse_finding(component, vuln, scan_id))

        return findings

    def _parse_finding(self, component: Component, vuln_data: dict, scan_id: str) -> VulnerabilityFinding:
        severity_val = "UNKNOWN"
        raw_sev = vuln_data.get("severity")
        if isinstance(raw_sev, list) and raw_sev:
            severity_val = raw_sev[0].get("score") or raw_sev[0].get("type") or "UNKNOWN"
        elif isinstance(raw_sev, str):
            severity_val = raw_sev

        return VulnerabilityFinding(
            scan_id=scan_id,
            component_id=component.id,
            vuln_id=vuln_data.get("id", "UNKNOWN"),
            aliases=vuln_data.get("aliases", []),
            summary=vuln_data.get("summary")
            or (vuln_data.get("details", "")[:200] if vuln_data.get("details") else None),
            severity=severity_val,
            references=[ref.get("url") for ref in vuln_data.get("references", []) if ref.get("url")],
            source="osv",
        )
