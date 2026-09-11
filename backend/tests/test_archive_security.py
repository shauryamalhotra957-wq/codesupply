"""Comprehensive security tests for archive validation and extraction."""

import zipfile
from pathlib import Path

import pytest

from app.core.config import Settings
from app.services.archive import ArchiveSecurityError, ArchiveService


@pytest.fixture
def archive_service(tmp_path):
    settings = Settings(
        MAX_UPLOAD_SIZE_MB=5,
        MAX_ARCHIVE_FILES=20,
        MAX_EXTRACTED_SIZE_MB=10,
        TEMP_DIR=str(tmp_path / "temp"),
    )
    return ArchiveService(settings)


@pytest.mark.asyncio
async def test_valid_zip_extraction(archive_service, tmp_path):
    """Test extracting a benign zip archive."""
    zip_path = tmp_path / "valid.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("package.json", '{"name": "test"}')
        zf.writestr("nested/file.txt", "hello nested")

    extracted = await archive_service.validate_and_extract(zip_path, "scan_1")
    assert extracted.exists()
    assert (extracted / "package.json").read_text() == '{"name": "test"}'
    assert (extracted / "nested" / "file.txt").read_text() == "hello nested"

    # Test cleanup
    archive_service.cleanup("scan_1")
    scan_dir = Path(archive_service.settings.TEMP_DIR) / "scan_1"
    assert not scan_dir.exists()


@pytest.mark.asyncio
async def test_corrupted_or_non_zip_rejected(archive_service, tmp_path):
    """Test that a non-zip file is rejected with INVALID_ARCHIVE."""
    bad_zip = tmp_path / "not_a_zip.zip"
    bad_zip.write_bytes(b"This is plain text, not a zip file.")

    with pytest.raises(ArchiveSecurityError) as exc_info:
        await archive_service.validate_and_extract(bad_zip, "scan_corrupt")
    assert exc_info.value.code == "INVALID_SIGNATURE"


@pytest.mark.asyncio
async def test_path_traversal_parent_dir_rejected(archive_service, tmp_path):
    """Test that ../ traversal attempts are blocked."""
    zip_path = tmp_path / "traversal.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("../evil.txt", "evil content")

    with pytest.raises(ArchiveSecurityError) as exc_info:
        await archive_service.validate_and_extract(zip_path, "scan_trav")
    assert exc_info.value.code == "PATH_TRAVERSAL"


@pytest.mark.asyncio
async def test_path_traversal_windows_backslash_rejected(archive_service, tmp_path):
    """Test that ..\\ backslash traversal attempts are blocked."""
    zip_path = tmp_path / "trav_win.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("..\\evil.txt", "evil content")

    with pytest.raises(ArchiveSecurityError) as exc_info:
        await archive_service.validate_and_extract(zip_path, "scan_win_trav")
    assert exc_info.value.code == "PATH_TRAVERSAL"


@pytest.mark.asyncio
async def test_absolute_posix_path_rejected(archive_service, tmp_path):
    """Test that absolute POSIX paths (/etc/passwd) are rejected."""
    zip_path = tmp_path / "abs_posix.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("/etc/passwd", "root:x:0:0")

    with pytest.raises(ArchiveSecurityError) as exc_info:
        await archive_service.validate_and_extract(zip_path, "scan_abs")
    assert exc_info.value.code == "DANGEROUS_PATH"


@pytest.mark.asyncio
async def test_absolute_windows_path_rejected(archive_service, tmp_path):
    """Test that Windows drive-letter absolute paths are rejected."""
    zip_path = tmp_path / "abs_win.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("C:\\Windows\\System32\\cmd.exe", "malicious")

    with pytest.raises(ArchiveSecurityError) as exc_info:
        await archive_service.validate_and_extract(zip_path, "scan_win_abs")
    assert exc_info.value.code == "DANGEROUS_PATH"


def test_null_byte_filename_rejected(archive_service, tmp_path):
    """Test that filenames with embedded null bytes are rejected."""
    info = zipfile.ZipInfo()
    info.filename = "valid.txt\x00.exe"
    with pytest.raises(ArchiveSecurityError) as exc_info:
        archive_service._validate_entry(info, tmp_path)
    assert exc_info.value.code == "DANGEROUS_PATH"


@pytest.mark.asyncio
async def test_file_count_limit(archive_service, tmp_path):
    """Test that archives exceeding MAX_ARCHIVE_FILES are rejected."""
    zip_path = tmp_path / "many_files.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for i in range(25):  # limit is 20
            zf.writestr(f"file_{i}.txt", f"data {i}")

    with pytest.raises(ArchiveSecurityError) as exc_info:
        await archive_service.validate_and_extract(zip_path, "scan_count")
    assert exc_info.value.code == "TOO_MANY_FILES"


@pytest.mark.asyncio
async def test_archive_bomb_uncompressed_size(tmp_path):
    """Test that archives exceeding MAX_EXTRACTED_SIZE_MB are rejected."""
    settings = Settings(
        MAX_UPLOAD_SIZE_MB=50,
        MAX_ARCHIVE_FILES=10,
        MAX_EXTRACTED_SIZE_MB=1,  # 1 MB max
        TEMP_DIR=str(tmp_path / "temp"),
    )
    svc = ArchiveService(settings)

    zip_path = tmp_path / "bomb.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # 2 MB of zeros compresses to a few KB
        zf.writestr("huge.txt", b"\x00" * (2 * 1024 * 1024))

    with pytest.raises(ArchiveSecurityError) as exc_info:
        await svc.validate_and_extract(zip_path, "scan_bomb")
    assert exc_info.value.code == "ARCHIVE_BOMB"
