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
