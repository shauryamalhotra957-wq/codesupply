import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

from scanner.parsers.base import BaseParser, ParsedDependency


class CargoParser(BaseParser):
    """
    Parses Rust Cargo.toml and Cargo.lock files.
    Extracts direct and transitive Rust dependencies, versions, and checksums.
    """

    def can_parse(self, filename: str) -> bool:
        lower = filename.lower()
        return lower == "cargo.toml" or lower.endswith("cargo.toml") or lower == "cargo.lock" or lower.endswith("cargo.lock")

    def parse(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        filename = file_path.name.lower()
        if filename == "cargo.toml" or filename.endswith("cargo.toml"):
            return self._parse_cargo_toml(file_path, relative_path)
        elif filename == "cargo.lock" or filename.endswith("cargo.lock"):
            return self._parse_cargo_lock(file_path, relative_path)
        return []

    def _parse_cargo_toml(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        deps: List[ParsedDependency] = []
        if tomllib is None:
            return self._regex_parse_cargo_toml(file_path, relative_path)

        try:
            with open(file_path, "rb") as f:
                data = tomllib.load(f)
        except Exception:
            return self._regex_parse_cargo_toml(file_path, relative_path)

        def extract_table(table: Dict[str, Any], scope: str):
            for name, val in table.items():
                if isinstance(val, str):
                    deps.append(
                        ParsedDependency(
                            name=name,
                            version=val if val.replace(".", "").isdigit() else None,
                            specifier=val,
                            ecosystem="cargo",
                            direct=True,
                            source_file=relative_path,
                            scope=scope,
                        )
                    )
                elif isinstance(val, dict):
                    version = val.get("version")
                    deps.append(
                        ParsedDependency(
                            name=name,
                            version=version if version and version.replace(".", "").isdigit() else None,
                            specifier=version,
                            ecosystem="cargo",
                            direct=True,
                            source_file=relative_path,
                            scope=scope,
                            metadata={"features": val.get("features", [])},
                        )
                    )

        if "dependencies" in data and isinstance(data["dependencies"], dict):
            extract_table(data["dependencies"], "required")

        if "dev-dependencies" in data and isinstance(data["dev-dependencies"], dict):
            extract_table(data["dev-dependencies"], "dev")

        if "build-dependencies" in data and isinstance(data["build-dependencies"], dict):
            extract_table(data["build-dependencies"], "build")

        return deps

    def _parse_cargo_lock(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        deps: List[ParsedDependency] = []
        if tomllib is None:
            return []

        try:
            with open(file_path, "rb") as f:
                data = tomllib.load(f)
        except Exception:
            return []

        packages = data.get("package", [])
        if not isinstance(packages, list):
            return deps

        for pkg in packages:
            if not isinstance(pkg, dict):
                continue
            name = pkg.get("name")
            version = pkg.get("version")
            if not name:
                continue

            checksum = pkg.get("checksum")
            child_deps = []
            for d in pkg.get("dependencies", []):
                if isinstance(d, str):
                    child_name = d.split(" ")[0]
                    child_deps.append(child_name)

            deps.append(
                ParsedDependency(
                    name=name,
                    version=str(version) if version else None,
                    specifier=f"=={version}" if version else None,
                    ecosystem="cargo",
                    direct=False,
                    source_file=relative_path,
                    integrity=f"sha256:{checksum}" if checksum else None,
                    dependencies=child_deps,
                )
            )

        return deps

    def _regex_parse_cargo_toml(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        deps: List[ParsedDependency] = []
        current_section = None
        dep_line_re = re.compile(r'^([a-zA-Z0-9_\-]+)\s*=\s*(?:"([^"]+)"|\{.*version\s*=\s*"([^"]+)".*\})')

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("[") and line.endswith("]"):
                        current_section = line[1:-1].strip()
                        continue
                    if current_section in ("dependencies", "dev-dependencies", "build-dependencies"):
                        match = dep_line_re.match(line)
                        if match:
                            name = match.group(1)
                            version = match.group(2) or match.group(3)
                            scope = "dev" if "dev" in current_section else ("build" if "build" in current_section else "required")
                            deps.append(
                                ParsedDependency(
                                    name=name,
                                    version=version,
                                    specifier=version,
                                    ecosystem="cargo",
                                    direct=True,
                                    source_file=relative_path,
                                    scope=scope,
                                )
                            )
        except Exception:
            pass
        return deps
