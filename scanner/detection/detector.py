import os
from pathlib import Path
from typing import Dict, List, Set

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
    "target",
    "vendor",
    ".tox",
    ".idea",
    ".vscode",
}

MANIFEST_ECOSYSTEM_MAP = {
    "requirements.txt": "pypi",
    "pyproject.toml": "pypi",
    "Pipfile": "pypi",
    "setup.py": "pypi",
    "package.json": "npm",
    "package-lock.json": "npm",
    "Cargo.toml": "cargo",
    "Cargo.lock": "cargo",
    "go.mod": "golang",
    "go.sum": "golang",
}


class ProjectDetectionResult:
    def __init__(self, root_dir: Path, ecosystems: List[str], manifest_files: List[Dict[str, str]]):
        self.root_dir = root_dir
        self.ecosystems = ecosystems
        self.manifest_files = manifest_files

    def to_dict(self) -> dict:
        return {
            "root_dir": str(self.root_dir),
            "ecosystems": self.ecosystems,
            "manifest_files": self.manifest_files,
        }


class ProjectDetector:
    """
    Detects package ecosystems and manifest files in an extracted project directory.
    Ignores generated / vendor directories.
    """

    @classmethod
    def detect(cls, root_path: Path | str) -> ProjectDetectionResult:
        root = Path(root_path).resolve()
        detected_ecosystems: Set[str] = set()
        manifest_files: List[Dict[str, str]] = []

        if not root.exists() or not root.is_dir():
            return ProjectDetectionResult(root, [], [])

        for dirpath, dirnames, filenames in os.walk(root):
            # Prune ignored directories in place
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]

            rel_dir = Path(dirpath).relative_to(root)

            for filename in filenames:
                lower_name = filename.lower()
                ecosystem = None

                if lower_name == "requirements.txt" or (
                    lower_name.startswith("requirements") and lower_name.endswith(".txt")
                ):
                    ecosystem = "pypi"
                elif lower_name == "pyproject.toml":
                    ecosystem = "pypi"
                elif lower_name == "pipfile":
                    ecosystem = "pypi"
                elif lower_name == "setup.py":
                    ecosystem = "pypi"
                elif lower_name == "package.json":
                    ecosystem = "npm"
                elif lower_name == "package-lock.json":
                    ecosystem = "npm"
                elif lower_name == "cargo.toml" or lower_name == "cargo.lock":
                    ecosystem = "cargo"
                elif lower_name == "go.mod" or lower_name == "go.sum":
                    ecosystem = "golang"

                if ecosystem:
                    detected_ecosystems.add(ecosystem)
                    rel_file_path = str(rel_dir / filename).replace("\\", "/")
                    if rel_file_path.startswith("./"):
                        rel_file_path = rel_file_path[2:]
                    manifest_files.append({
                        "file_name": filename,
                        "relative_path": rel_file_path,
                        "full_path": str(Path(dirpath) / filename),
                        "ecosystem": ecosystem,
                    })

        return ProjectDetectionResult(
            root_dir=root,
            ecosystems=sorted(list(detected_ecosystems)),
            manifest_files=manifest_files,
        )
