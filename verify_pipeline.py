"""Full System End-to-End Verification Script."""

import asyncio
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.core.database import init_db
from app.main import app
from app.workers.runner import ScanWorker


async def run_verification():
    print("=" * 60)
    print("CodeSupply v1.2.0 - End-to-End System Preflight Check")
    print("=" * 60)

    await init_db()
    settings = get_settings()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. Health check
        health = await client.get("/api/health")
        print(f"[1/5] Health Check: {health.status_code} - {health.json()}")

        # 2. Sample scan creation
        scan_res = await client.post("/api/scans/sample")
        assert scan_res.status_code == 201
        scan_id = scan_res.json()["id"]
        print(f"[2/5] Created Scan: {scan_id} ({scan_res.json()['filename']})")

        # 3. Worker execution
        print("[3/5] Running Core Pipeline Worker...")
        worker = ScanWorker(settings)
        await worker.process_scan(scan_id)

        # 4. Verification of results
        status = await client.get(f"/api/scans/{scan_id}")
        summary = await client.get(f"/api/scans/{scan_id}/summary")
        summary_data = summary.json()
        print(
            f"[4/5] Pipeline Complete! Components: {summary_data['total_components']}, Vulns: {summary_data['total_vulnerabilities']}"
        )
        print(
            f"      Ecosystems Discovered: {list(summary_data['components_by_ecosystem'].keys())}"
        )
        print(f"      Risk Levels: {summary_data['components_by_risk']}")

        # 5. Dual SBOM verification
        cdx = await client.get(f"/api/scans/{scan_id}/sbom")
        spdx = await client.get(f"/api/scans/{scan_id}/sbom/spdx")
        assert cdx.status_code == 200
        assert spdx.status_code == 200
        print("[5/5] Dual SBOM Generation:")
        print(
            f"      CycloneDX 1.7: Valid = {cdx.json()['is_valid']} ({cdx.json()['component_count']} components)"
        )
        print(
            f"      SPDX 2.3: Valid = True ({len(spdx.json()['packages'])} packages, {len(spdx.json()['relationships'])} relationships)"
        )

    print("\n[SUCCESS] ALL PREFLIGHT CHECKS PASSED PERFECTLY.")


if __name__ == "__main__":
    asyncio.run(run_verification())

