import io
import zipfile
from pathlib import Path
import pytest

from scanner.security.safe_extractor import SafeExtractionError, SafeExtractor


def test_safe_zip_extraction(tmp_path: Path):
    # Create valid harmless zip
    zip_path = tmp_path / "valid.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("requirements.txt", "fastapi==0.110.0\n")
        zf.writestr("src/main.py", "print('hello')\n")

    dest_dir = tmp_path / "extracted"
    extracted = SafeExtractor.extract_to_dir(zip_path, dest_dir)
    assert (extracted / "requirements.txt").exists()
    assert (extracted / "src" / "main.py").exists()


def test_zipslip_path_traversal_prevention(tmp_path: Path):
    # Create malicious zip with relative traversal '../escape.txt'
    zip_path = tmp_path / "malicious.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("../escape.txt", "MALICIOUS CONTENT")

    dest_dir = tmp_path / "safe_dest"

    with pytest.raises(SafeExtractionError) as exc_info:
        SafeExtractor.extract_to_dir(zip_path, dest_dir)

    assert "traversal" in str(exc_info.value).lower() or "escape" in str(exc_info.value).lower()


def test_zip_invalid_extension(tmp_path: Path):
    bad_file = tmp_path / "payload.exe"
    bad_file.write_bytes(b"MZ123")

    with pytest.raises(SafeExtractionError) as exc_info:
        SafeExtractor.validate_archive(bad_file)

    assert "extension" in str(exc_info.value).lower()
