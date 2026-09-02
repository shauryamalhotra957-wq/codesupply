import os
import shutil
import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

# Security limits for untrusted archive uploads
MAX_ARCHIVE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB compressed
MAX_UNCOMPRESSED_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB uncompressed
MAX_FILE_COUNT = 5000
ALLOWED_EXTENSIONS = {".zip"}


class SafeExtractionError(Exception):
    """Raised when an archive fails security validation or extraction."""
    pass


class SafeExtractor:
    """
    Safely inspects and extracts untrusted ZIP archives.
    Protects against ZipSlip (path traversal), Zip Bombs, and unsafe file types.
    Never executes any extracted content.
    """

    @staticmethod
    def validate_archive(zip_path: Path | str) -> None:
        path = Path(zip_path)
        if not path.exists():
            raise SafeExtractionError(f"Archive file not found: {path}")

        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            raise SafeExtractionError(f"Unsupported file extension: {path.suffix}. Only .zip archives are permitted.")

        file_size = path.stat().st_size
        if file_size > MAX_ARCHIVE_SIZE_BYTES:
            raise SafeExtractionError(
                f"Archive exceeds maximum allowed size of {MAX_ARCHIVE_SIZE_BYTES // (1024*1024)}MB "
                f"(actual: {file_size // (1024*1024)}MB)"
            )

        if not zipfile.is_zipfile(path):
            raise SafeExtractionError("Invalid or corrupted ZIP archive format.")

        total_uncompressed_size = 0

        with zipfile.ZipFile(path, "r") as zf:
            infolist = zf.infolist()
            total_files = len(infolist)
            if total_files > MAX_FILE_COUNT:
                raise SafeExtractionError(
                    f"Archive contains {total_files} entries, exceeding limit of {MAX_FILE_COUNT}"
                )

            for info in infolist:
                # Zip Slip checks: detect directory traversal attempts
                filename = info.filename
                # Check for path traversal components
                parts = Path(filename).parts
                if ".." in parts or filename.startswith("/") or filename.startswith("\\"):
                    raise SafeExtractionError(
                        f"Potentially malicious path traversal detected in ZIP entry: '{filename}'"
                    )

                total_uncompressed_size += info.file_size
                if total_uncompressed_size > MAX_UNCOMPRESSED_SIZE_BYTES:
                    raise SafeExtractionError(
                        f"Archive uncompressed content exceeds limit of {MAX_UNCOMPRESSED_SIZE_BYTES // (1024*1024)}MB"
                    )

    @classmethod
    def extract_to_dir(cls, zip_path: Path | str, destination_dir: Path | str) -> Path:
        dest = Path(destination_dir).resolve()
        dest.mkdir(parents=True, exist_ok=True)
        cls.validate_archive(zip_path)

        with zipfile.ZipFile(zip_path, "r") as zf:
            for member in zf.infolist():
                # Double-check path resolution
                target_path = (dest / member.filename).resolve()
                try:
                    # Target path must be strictly within destination dir
                    target_path.relative_to(dest)
                except ValueError:
                    raise SafeExtractionError(
                        f"Security violation: Attempted path escape '{member.filename}' outside destination"
                    )

                if member.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as src_file, open(target_path, "wb") as out_file:
                        shutil.copyfileobj(src_file, out_file)

        return dest

    @classmethod
    @contextmanager
    def safe_temp_workspace(cls, zip_path: Path | str) -> Generator[Path, None, None]:
        temp_dir = Path(tempfile.mkdtemp(prefix="codesupply_scan_"))
        try:
            extracted_path = cls.extract_to_dir(zip_path, temp_dir)
            yield extracted_path
        finally:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
