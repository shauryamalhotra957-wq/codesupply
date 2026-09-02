import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from scanner.parsers.base import BaseParser, ParsedDependency


class NodeParser(BaseParser):
    """
    Parses Node.js package.json and package-lock.json (v1, v2, v3).
    Extracts direct manifests, locked exact versions, integrity hashes,
    and transitive sub-dependency relationships.
    """

    def can_parse(self, filename: str) -> bool:
        lower = filename.lower()
        return lower in ("package.json", "package-lock.json")

    def parse(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        filename = file_path.name.lower()
        if filename == "package.json":
            return self._parse_package_json(file_path, relative_path)
        elif filename == "package-lock.json":
            return self._parse_package_lock_json(file_path, relative_path)
        return []

    def _parse_package_json(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        dependencies: List[ParsedDependency] = []
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            data = json.loads(content)

            scopes_map = [
                ("dependencies", "required"),
                ("devDependencies", "dev"),
                ("peerDependencies", "optional"),
                ("optionalDependencies", "optional"),
            ]

            for section_key, scope_name in scopes_map:
                section_deps = data.get(section_key, {})
                if isinstance(section_deps, dict):
                    for name, spec in section_deps.items():
                        if not isinstance(name, str) or not isinstance(spec, str):
                            continue

                        # Extract exact version if spec is pinned without range markers
                        version = None
                        clean_spec = spec.strip()
                        if re.match(r"^[0-9]+\.[0-9]+", clean_spec):
                            version = clean_spec

                        dependencies.append(
                            ParsedDependency(
                                name=name,
                                version=version,
                                specifier=clean_spec,
                                ecosystem="npm",
                                direct=True,
                                source_file=relative_path,
                                scope=scope_name,
                            )
                        )
        except Exception:
            pass
        return dependencies

    def _parse_package_lock_json(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        dependencies: List[ParsedDependency] = []
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            data = json.loads(content)

            lockfile_version = data.get("lockfileVersion", 1)

            # Direct dependencies declared at root of package-lock.json if available
            root_packages = data.get("packages", {}).get("", {})
            root_direct_names = set()
            if isinstance(root_packages, dict):
                root_direct_names.update(root_packages.get("dependencies", {}).keys())
                root_direct_names.update(root_packages.get("devDependencies", {}).keys())

            # Also check top-level dependencies for v1
            if not root_direct_names and "dependencies" in data:
                # In v1, top-level keys in 'dependencies' are direct
                root_direct_names.update(data.get("dependencies", {}).keys())

            # Format: lockfileVersion 2 or 3 ('packages' map)
            if "packages" in data and isinstance(data["packages"], dict):
                for pkg_path, pkg_data in data["packages"].items():
                    if not pkg_path or pkg_path == "":
                        continue  # Root project descriptor
                    if not isinstance(pkg_data, dict):
                        continue

                    # Extract clean package name from node_modules path
                    # e.g. "node_modules/express" -> "express"
                    # "node_modules/@types/node" -> "@types/node"
                    # "node_modules/foo/node_modules/bar" -> "bar"
                    pkg_name = self._extract_name_from_node_modules_path(pkg_path)
                    if not pkg_name:
                        pkg_name = pkg_data.get("name", "")

                    if not pkg_name:
                        continue

                    version = pkg_data.get("version")
                    resolved = pkg_data.get("resolved")
                    integrity = pkg_data.get("integrity")
                    license_str = pkg_data.get("license")

                    is_dev = pkg_data.get("dev", False)
                    is_optional = pkg_data.get("optional", False)
                    scope = "dev" if is_dev else ("optional" if is_optional else "required")

                    # Sub-dependencies declared in this package
                    sub_deps = list(pkg_data.get("dependencies", {}).keys())

                    is_direct = pkg_name in root_direct_names and ("/" not in pkg_path.replace("node_modules/", ""))

                    dependencies.append(
                        ParsedDependency(
                            name=pkg_name,
                            version=version,
                            specifier=f"=={version}" if version else None,
                            ecosystem="npm",
                            direct=is_direct,
                            source_file=relative_path,
                            scope=scope,
                            license=license_str if isinstance(license_str, str) else None,
                            integrity=integrity,
                            resolved_url=resolved,
                            dependencies=sub_deps,
                            metadata={"lock_path": pkg_path, "lockfile_version": lockfile_version},
                        )
                    )

            # Fallback / v1 format ('dependencies' recursive tree)
            elif "dependencies" in data and isinstance(data["dependencies"], dict):
                self._parse_v1_dependencies(
                    data["dependencies"],
                    relative_path,
                    dependencies,
                    is_root_level=True,
                    lockfile_version=lockfile_version,
                )

        except Exception:
            pass
        return dependencies

    def _parse_v1_dependencies(
        self,
        deps_dict: Dict[str, Any],
        source_file: str,
        result_list: List[ParsedDependency],
        is_root_level: bool,
        lockfile_version: int,
    ) -> None:
        for name, info in deps_dict.items():
            if not isinstance(info, dict):
                continue

            version = info.get("version")
            resolved = info.get("resolved")
            integrity = info.get("integrity")
            is_dev = info.get("dev", False)
            scope = "dev" if is_dev else "required"

            sub_deps = list(info.get("requires", {}).keys())

            result_list.append(
                ParsedDependency(
                    name=name,
                    version=version,
                    specifier=f"=={version}" if version else None,
                    ecosystem="npm",
                    direct=is_root_level,
                    source_file=source_file,
                    scope=scope,
                    integrity=integrity,
                    resolved_url=resolved,
                    dependencies=sub_deps,
                    metadata={"lockfile_version": lockfile_version},
                )
            )

            # Recurse for nested dependencies if any
            nested = info.get("dependencies")
            if isinstance(nested, dict):
                self._parse_v1_dependencies(
                    nested,
                    source_file,
                    result_list,
                    is_root_level=False,
                    lockfile_version=lockfile_version,
                )

    def _extract_name_from_node_modules_path(self, path: str) -> Optional[str]:
        # Clean path separators
        clean_path = path.replace("\\", "/")
        if "node_modules/" not in clean_path:
            return None

        # Take last occurrence of node_modules/
        last_idx = clean_path.rfind("node_modules/")
        sub = clean_path[last_idx + len("node_modules/") :]

        # Check for scoped package: @org/pkg
        parts = sub.split("/")
        if len(parts) >= 2 and parts[0].startswith("@"):
            return f"{parts[0]}/{parts[1]}"
        elif len(parts) >= 1:
            return parts[0]
        return None
