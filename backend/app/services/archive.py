"""Secure ZIP archive handling — treats all uploads as hostile."""

import re
import shutil
import zipfile
from pathlib import Path

from app.core.config import Settings


class ArchiveSecurityError(Exception):
    """Raised when archive security validation fails."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


# Patterns that indicate path traversal
_TRAVERSAL_PATTERNS = [
    "..",
    "\\",
]

# Absolute path indicators
_ABSOLUTE_PATTERNS = re.compile(r"^(/|[A-Za-z]:[/\\])")


class ArchiveService:
    """Validates and extracts ZIP archives with comprehensive security checks.

    Security measures:
    - File size limits
    - File count limits
    - Uncompressed size limits (archive bomb protection)
    - Path traversal prevention via resolve() + containment check
    - Absolute path rejection
    - Dangerous path detection
    - Isolated temporary directory per scan
    - No code execution guarantee
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    async def validate_and_extract(self, file_path: Path, scan_id: str) -> Path:
        """Validate ZIP and extract to isolated temp dir.

        Args:
            file_path: Path to the uploaded ZIP file
            scan_id: Unique scan identifier for isolation

        Returns:
            Path to extraction directory

        Raises:
            ArchiveSecurityError: On any security validation failure
        """
        # File size check
        file_size = file_path.stat().st_size
        max_bytes = self.settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise ArchiveSecurityError(
                "FILE_TOO_LARGE",
                f"This archive exceeds the {self.settings.MAX_UPLOAD_SIZE_MB} MB upload limit.",
            )

        # Validate ZIP format
        if not zipfile.is_zipfile(file_path):
            raise ArchiveSecurityError(
                "INVALID_ARCHIVE",
                "We couldn't read this archive. The file may be corrupted or unsupported.",
            )

        # Extract to a subdirectory separate from the upload
        extraction_path = Path(self.settings.TEMP_DIR) / scan_id / "extracted"
        extraction_path.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                infos = zf.infolist()

                # File count check
                if len(infos) > self.settings.MAX_ARCHIVE_FILES:
                    raise ArchiveSecurityError(
                        "TOO_MANY_FILES",
                        f"Archive contains {len(infos)} entries, exceeding the {self.settings.MAX_ARCHIVE_FILES} file limit.",
                    )

                # Uncompressed size check (archive bomb protection)
                total_uncompressed = sum(info.file_size for info in infos)
                max_extracted = self.settings.MAX_EXTRACTED_SIZE_MB * 1024 * 1024
                if total_uncompressed > max_extracted:
                    raise ArchiveSecurityError(
                        "ARCHIVE_BOMB",
                        f"Archive uncompressed size ({total_uncompressed // (1024 * 1024)} MB) exceeds the {self.settings.MAX_EXTRACTED_SIZE_MB} MB limit.",
                    )

                # Compression ratio check
                if file_size > 0 and total_uncompressed / file_size > 100:
                    raise ArchiveSecurityError(
                        "ARCHIVE_BOMB",
                        "This archive has a suspiciously high compression ratio and was rejected.",
                    )

                # Validate each entry
                for info in infos:
                    self._validate_entry(info, extraction_path)

                # Safe to extract
                zf.extractall(extraction_path)

            return extraction_path

        except zipfile.BadZipFile:
            self._cleanup_extraction(extraction_path)
            raise ArchiveSecurityError(
                "INVALID_ARCHIVE",
                "We couldn't read this archive. The file may be corrupted or unsupported.",
            )
        except ArchiveSecurityError:
            self._cleanup_extraction(extraction_path)
            raise
        except Exception as e:
            self._cleanup_extraction(extraction_path)
            raise ArchiveSecurityError(
                "EXTRACTION_FAILED",
                "An error occurred while processing this archive.",
            ) from e

    def _validate_entry(self, info: zipfile.ZipInfo, base_dir: Path) -> None:
        """Validate a single ZIP entry for security issues."""
        filename = info.filename

        # Check for empty filename or null bytes
        if not filename or not filename.strip() or "\x00" in filename:
            raise ArchiveSecurityError(
                "DANGEROUS_PATH",
                "This archive contains entries with invalid filenames.",
            )

        # Check for absolute paths
        if _ABSOLUTE_PATTERNS.match(filename):
            raise ArchiveSecurityError(
                "DANGEROUS_PATH",
                "This archive contains unsafe paths and was rejected before extraction.",
            )

        # Check for path traversal components
        parts = filename.replace("\\", "/").split("/")
        for part in parts:
            if part == "..":
                raise ArchiveSecurityError(
                    "PATH_TRAVERSAL",
                    "This archive contains unsafe paths and was rejected before extraction.",
                )

        # Use resolve() to verify containment — the definitive check
        if not self._is_safe_path(base_dir, filename):
            raise ArchiveSecurityError(
                "PATH_TRAVERSAL",
                "This archive contains unsafe paths and was rejected before extraction.",
            )

    def _is_safe_path(self, base_dir: Path, entry_path: str) -> bool:
        """Check path doesn't escape base directory using resolve().

        Uses Path.resolve() for canonicalization, NOT string prefix tricks.
        """
        try:
            base_resolved = base_dir.resolve()
            full_path = (base_dir / entry_path).resolve()
            # Use os.path to handle platform differences
            return str(full_path).startswith(str(base_resolved))
        except (OSError, ValueError):
            return False

    def _cleanup_extraction(self, path: Path) -> None:
        """Remove extraction directory on failure."""
        try:
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)
        except Exception:
            pass

    def cleanup(self, scan_id: str) -> None:
        """Remove all artifacts for a scan."""
        scan_dir = Path(self.settings.TEMP_DIR) / scan_id
        try:
            if scan_dir.exists():
                shutil.rmtree(scan_dir, ignore_errors=True)
        except Exception:
            pass
