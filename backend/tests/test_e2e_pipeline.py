"""Full End-to-End Pipeline test:
Upload/Sample -> Extraction -> Discovery -> Parsing -> Normalizing -> Resolving -> SBOM Generation -> SBOM Validation -> Vulnerability Analysis -> Risk Analysis -> Dashboard/Graph/SBOM API
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.core.database import init_db
from app.main import app
from app.workers.runner import ScanWorker


@pytest.mark.asyncio
async def test_full_e2e_scan_pipeline():
    await init_db()
    settings = get_settings()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Create sample scan
        create_resp = await client.post("/api/scans/sample")
        assert create_resp.status_code == 201
        scan_data = create_resp.json()
        scan_id = scan_data["id"]
        assert scan_data["status"] == "queued"

        # 2. Worker processes the scan
        worker = ScanWorker(settings)
        await worker.process_scan(scan_id)

        # 3. Check scan status is complete
        status_resp = await client.get(f"/api/scans/{scan_id}")
        assert status_resp.status_code == 200
        completed_scan = status_resp.json()
        assert completed_scan["status"] == "complete", f"Scan failed: {completed_scan.get('error_message')}"
        assert completed_scan["total_components"] > 0
        assert completed_scan["total_manifests"] >= 5

        # 4. Check summary
        summary_resp = await client.get(f"/api/scans/{scan_id}/summary")
        assert summary_resp.status_code == 200
        summary = summary_resp.json()
        assert summary["total_components"] == completed_scan["total_components"]
        assert "npm" in summary["components_by_ecosystem"]
        assert "pypi" in summary["components_by_ecosystem"]
        assert "maven" in summary["components_by_ecosystem"]
        assert summary["sbom_valid"] is True

        # 5. Check components list
        comps_resp = await client.get(f"/api/scans/{scan_id}/components")
        assert comps_resp.status_code == 200
        comps = comps_resp.json()
        assert comps["total"] > 0
        assert len(comps["items"]) > 0

        # Verify evidence is attached to components
        sample_comp = comps["items"][0]
        assert len(sample_comp["evidence"]) > 0
        assert sample_comp["purl"] is not None or sample_comp["version_confidence"] != "exact"

        # 6. Check dependency graph
        graph_resp = await client.get(f"/api/scans/{scan_id}/graph")
        assert graph_resp.status_code == 200
        graph = graph_resp.json()
        assert len(graph["nodes"]) > 0
        assert len(graph["edges"]) > 0

        # 7. Check SBOM endpoint
        sbom_resp = await client.get(f"/api/scans/{scan_id}/sbom")
        assert sbom_resp.status_code == 200
        sbom = sbom_resp.json()
        assert sbom["format"] == "CycloneDX"
        assert sbom["spec_version"] == "1.7"
        assert sbom["is_valid"] is True
        assert len(sbom["content"]["components"]) == summary["total_components"]

        # 8. Check SBOM download
        dl_resp = await client.get(f"/api/scans/{scan_id}/download/sbom")
        assert dl_resp.status_code == 200
        assert "application/json" in dl_resp.headers["content-type"]
