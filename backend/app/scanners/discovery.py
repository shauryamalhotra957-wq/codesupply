import os
from dataclasses import dataclass
from pathlib import Path

MANIFEST_PATTERNS = {
    "npm": {"package.json", "package-lock.json"},
    "python": {"requirements.txt", "pyproject.toml"},
    "maven": {"pom.xml"},
    "golang": {"go.mod"},
    "cargo": {"Cargo.toml"},
}

DETECTION_ONLY = {
    "go_sum": {"go.sum"},
    "cargo_lock": {"Cargo.lock"},
    "csharp": {"*.csproj", "*.sln", "packages.config"},
    "php": {"composer.json", "composer.lock"},
}

IGNORE_DIRS = {
    "node_modules",
    ".git",
    "__pycache__",
    "target",
    "dist",
    "build",
    ".tox",
    ".venv",
    "venv",
    ".env",
}


@dataclass
class DiscoveredManifest:
    path: str  # relative to extraction root
    ecosystem: str
    manifest_type: str  # e.g. "lockfile", "manifest", "build"
    is_supported: bool
    file_size: int


def discover_manifests(extraction_path: Path) -> list[DiscoveredManifest]:
    """Recursively find all manifests, skipping ignored dirs."""
    manifests = []

    for root, dirs, files in os.walk(extraction_path):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        rel_root = Path(root).relative_to(extraction_path)

        for file in files:
            file_path = rel_root / file
            file_size = (Path(root) / file).stat().st_size

            # Check supported patterns
            for ecosystem, patterns in MANIFEST_PATTERNS.items():
                if file in patterns:
                    manifest_type = "lockfile" if "lock" in file else "manifest"
                    manifests.append(
                        DiscoveredManifest(
                            path=str(file_path).replace("\\", "/"),
                            ecosystem=ecosystem,
                            manifest_type=manifest_type,
                            is_supported=True,
                            file_size=file_size,
                        )
                    )
                    break

            # Check detection-only patterns
            for ecosystem, patterns in DETECTION_ONLY.items():
                # Simplified check for detection-only
                match = False
                for pattern in patterns:
                    if pattern.startswith("*.") and file.endswith(pattern[2:]) or file == pattern:
                        match = True

                if match:
                    manifest_type = "lockfile" if "lock" in file or "sum" in file else "manifest"
                    manifests.append(
                        DiscoveredManifest(
                            path=str(file_path).replace("\\", "/"),
                            ecosystem=ecosystem,
                            manifest_type=manifest_type,
                            is_supported=False,
                            file_size=file_size,
                        )
                    )
                    break

    return manifests
