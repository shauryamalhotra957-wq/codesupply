import zipfile

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services.archive import ArchiveSecurityError, ArchiveService

client = TestClient(app)


def test_security_headers():
    response = client.get("/api/scans")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Strict-Transport-Security") == "max-age=31536000; includeSubDomains"
    assert response.headers.get("Content-Security-Policy") == "default-src 'self'"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert response.headers.get("Permissions-Policy") == "camera=(), microphone=(), geolocation=()"


def test_docs_csp_allows_cdn():
    response = client.get("/docs")
    assert response.status_code == 200
    csp = response.headers.get("Content-Security-Policy", "")
    assert "cdn.jsdelivr.net" in csp


def test_rate_limiting():
    # The rate limiter works on IP. We'll simulate 5 uploads.
    # We use a custom client IP if needed, but TestClient uses a default one ("testclient").
    # We'll just loop 5 times, shouldn't get 429. The 6th should get 429.

    for _ in range(5):
        response = client.post("/api/scans", files={"file": ("test.zip", b"PK\x03\x04")})
        assert response.status_code != 429

    response = client.post("/api/scans", files={"file": ("test.zip", b"PK\x03\x04")})
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "TOO_MANY_REQUESTS"


@pytest.mark.asyncio
async def test_zip_magic_bytes_validation(tmp_path):
    settings = get_settings()
    service = ArchiveService(settings)

    fake_zip = tmp_path / "fake.zip"
    fake_zip.write_bytes(b"Not a zip file")

    with pytest.raises(ArchiveSecurityError) as exc_info:
        await service.validate_and_extract(fake_zip, "test_scan_id")

    assert exc_info.value.code == "INVALID_SIGNATURE"


@pytest.mark.asyncio
async def test_path_traversal_rejection(tmp_path):
    settings = get_settings()
    service = ArchiveService(settings)

    malicious_zip = tmp_path / "malicious.zip"
    with zipfile.ZipFile(malicious_zip, "w") as zf:
        zf.writestr("../../../etc/passwd", b"malicious content")

    with pytest.raises(ArchiveSecurityError) as exc_info:
        await service.validate_and_extract(malicious_zip, "test_scan_id")

    assert exc_info.value.code in ("PATH_TRAVERSAL", "DANGEROUS_PATH")


def test_scan_id_validation():
    # Valid hex (32 chars)
    valid_id = "a" * 32
    response = client.get(f"/api/scans/{valid_id}")
    # It might be 404 (not found), but shouldn't be 400 (invalid)
    assert response.status_code != 400

    # Invalid hex (too short)
    invalid_id = "abc"
    response = client.get(f"/api/scans/{invalid_id}")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_SCAN_ID"

    # Invalid characters
    invalid_id2 = "z" * 32
    response = client.get(f"/api/scans/{invalid_id2}")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_SCAN_ID"
