import json
from pathlib import Path
from typing import Any, Dict, List

from scanner.parsers.base import BaseParser, ParsedDependency


class ComposerParser(BaseParser):
    """
    Parses PHP composer.json and composer.lock files.
    Extracts direct and transitive PHP dependencies, versions, licenses, and dependencies.
    """

    def can_parse(self, filename: str) -> bool:
        lower = filename.lower()
        return (
            lower == "composer.json"
            or lower.endswith("composer.json")
            or lower == "composer.lock"
            or lower.endswith("composer.lock")
        )

    def parse(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        filename = file_path.name.lower()
        if filename == "composer.lock" or filename.endswith("composer.lock"):
            return self._parse_composer_lock(file_path, relative_path)
        elif filename == "composer.json" or filename.endswith("composer.json"):
            return self._parse_composer_json(file_path, relative_path)
        return []

    def _parse_composer_json(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        """Parses direct dependencies from composer.json."""
        deps: List[ParsedDependency] = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return deps

        def add_deps(dep_dict: Dict[str, Any], scope: str):
            for name, spec in dep_dict.items():
                if name.lower() == "php" or name.startswith("ext-"):
                    continue
                version = None
                spec_str = str(spec)
                if spec_str and spec_str[0].isdigit():
                    version = spec_str
                deps.append(
                    ParsedDependency(
                        name=name,
                        version=version,
                        specifier=spec_str,
                        ecosystem="composer",
                        direct=True,
                        source_file=relative_path,
                        scope=scope,
                    )
                )

        if "require" in data and isinstance(data["require"], dict):
            add_deps(data["require"], "required")
        if "require-dev" in data and isinstance(data["require-dev"], dict):
            add_deps(data["require-dev"], "dev")

        return deps

    def _parse_composer_lock(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        """Parses resolved dependencies from composer.lock."""
        deps: List[ParsedDependency] = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return deps

        def process_package_list(packages: List[Dict[str, Any]], scope: str):
            for pkg in packages:
                name = pkg.get("name", "")
                if not name:
                    continue
                raw_version = pkg.get("version", "").lstrip("v")
                license_val = None
                if pkg.get("license") and isinstance(pkg["license"], list) and len(pkg["license"]) > 0:
                    license_val = pkg["license"][0]
                elif isinstance(pkg.get("license"), str):
                    license_val = pkg["license"]

                resolved_url = None
                if pkg.get("source") and isinstance(pkg["source"], dict):
                    resolved_url = pkg["source"].get("url")

                # Child dependencies
                child_deps = []
                if "require" in pkg and isinstance(pkg["require"], dict):
                    for req_name in pkg["require"].keys():
                        if req_name.lower() != "php" and not req_name.startswith("ext-"):
                            child_deps.append(req_name)

                deps.append(
                    ParsedDependency(
                        name=name,
                        version=raw_version,
                        specifier=f"=={raw_version}" if raw_version else None,
                        ecosystem="composer",
                        direct=(scope == "required"),
                        source_file=relative_path,
                        scope=scope,
                        license=license_val,
                        resolved_url=resolved_url,
                        dependencies=child_deps,
                    )
                )

        if "packages" in data and isinstance(data["packages"], list):
            process_package_list(data["packages"], "required")
        if "packages-dev" in data and isinstance(data["packages-dev"], list):
            process_package_list(data["packages-dev"], "dev")

        return deps
