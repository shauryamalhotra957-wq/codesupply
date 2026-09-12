"""API integration tests for CodeSupply endpoints."""

import io
import zipfile

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.database import init_db
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await init_db()


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("ok", "degraded")
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_create_scan_non_zip_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("test.txt", b"plain text", "text/plain")}
        response = await client.post("/api/scans", files=files)
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "INVALID_FILE_TYPE"


@pytest.mark.asyncio
async def test_create_scan_valid_zip():
    # Build a small zip
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("package.json", '{"name": "test-pkg"}')

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("project.zip", buf.getvalue(), "application/zip")}
        response = await client.post("/api/scans", files=files)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "queued"
        assert data["filename"] == "project.zip"

        scan_id = data["id"]
        # Query scan status
        get_resp = await client.get(f"/api/scans/{scan_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == scan_id


@pytest.mark.asyncio
async def test_create_sample_scan():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/scans/sample")
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "queued"
        assert data["filename"] == "demo-project.zip"


@pytest.mark.asyncio
async def test_get_nonexistent_scan_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/scans/aabbccdd11223344aabbccdd11223344")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "SCAN_NOT_FOUND"


@pytest.mark.asyncio
async def test_vex_and_remediations_and_csv_endpoints():
    import uuid

    from app.core.database import async_session_factory
    from app.models.models import Component, Scan, VulnerabilityFinding

    test_id = uuid.uuid4().hex
    c_id = uuid.uuid4().hex
    v_id = uuid.uuid4().hex
    async with async_session_factory() as session:
        scan = Scan(
            id=test_id,
            status="complete",
            filename="app.zip",
            project_name="app",
            file_size=1024,
            total_components=1,
            total_vulnerabilities=1,
        )
        comp = Component(
            id=c_id,
            scan_id=test_id,
            name="lodash",
            version="4.17.15",
            ecosystem="npm",
            package_manager="npm",
            dependency_type="direct",
            version_confidence="exact",
            normalized_name="lodash",
            purl="pkg:npm/lodash@4.17.15",
            license="MIT",
            risk_level="high",
            source_file="package.json",
        )
        vuln = VulnerabilityFinding(
            id=v_id,
            scan_id=test_id,
            component_id=c_id,
            vuln_id="GHSA-p6mc-m468-83gw",
            severity="high",
            cvss_score=7.4,
            fixed_version="4.17.21",
            source="osv",
        )
        session.add_all([scan, comp, vuln])
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Test VEX JSON endpoint
        vex_res = await client.get(f"/api/scans/{test_id}/vex")
        assert vex_res.status_code == 200
        vex_data = vex_res.json()
        assert vex_data["bomFormat"] == "CycloneDX"
        assert len(vex_data["vulnerabilities"]) == 1
        assert vex_data["vulnerabilities"][0]["id"] == "GHSA-p6mc-m468-83gw"

        # 2. Test VEX Download endpoint
        vex_dl = await client.get(f"/api/scans/{test_id}/download/vex")
        assert vex_dl.status_code == 200
        assert "application/json" in vex_dl.headers["content-type"]
        assert "attachment" in vex_dl.headers["content-disposition"]

        # 3. Test Remediations endpoint
        rem_res = await client.get(f"/api/scans/{test_id}/remediations")
        assert rem_res.status_code == 200
        rem_data = rem_res.json()
        assert rem_data["total_remediations"] == 1
        assert rem_data["remediations"][0]["component_name"] == "lodash"
        assert rem_data["remediations"][0]["target_version"] == "4.17.21"
        assert "npm install lodash@4.17.21" in rem_data["remediations"][0]["upgrade_command"]

        # 4. Test CSV Export endpoint
        csv_res = await client.get(f"/api/scans/{test_id}/export/csv")
        assert csv_res.status_code == 200
        assert "text/csv" in csv_res.headers["content-type"]
        csv_text = csv_res.text
        assert "lodash" in csv_text
        assert "pkg:npm/lodash@4.17.15" in csv_text

        # 5. Test AI Component Explanation endpoint
        explain_res = await client.post(f"/api/scans/{test_id}/components/{c_id}/explain")
        assert explain_res.status_code == 200
        explain_data = explain_res.json()
        assert explain_data["component_id"] == c_id
        assert explain_data["component_name"] == "lodash"
        assert "summary" in explain_data
        assert "why_it_matters" in explain_data
        assert "what_to_do" in explain_data
        assert "AI-assisted explanation" in explain_data["label"]
