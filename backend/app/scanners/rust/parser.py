"""Rust Cargo.toml parser — parses Cargo manifest files."""

import toml

from app.services.normalizer import ParsedPackage, ParsedRelationship


class RustParser:
    """Parses Cargo.toml files to extract crate dependencies.

    Supports:
    - [dependencies] section
    - [dev-dependencies] section
    - [build-dependencies] section
    - Simple string format: name = "version"
    - Inline table format: name = { version = "1.0", features = ["derive"] }
    - Workspace dependencies (detected, marked as unknown version)
    """

    def parse_cargo_toml(self, content: str, file_path: str) -> list[ParsedPackage]:
        """Parse Cargo.toml and return packages."""
        try:
            data = toml.loads(content)
        except Exception:
            return []

        packages = []

        # Parse each dependency section
        section_map = {
            "dependencies": "direct",
            "dev-dependencies": "dev",
            "build-dependencies": "direct",
        }

        for section, dep_type in section_map.items():
            deps = data.get(section, {})
            if not isinstance(deps, dict):
                continue

            for name, spec in deps.items():
                pkg = self._parse_dependency(name, spec, dep_type, file_path, section)
                if pkg:
                    packages.append(pkg)

        # Check target-specific dependencies: [target.'cfg(...)'.dependencies]
        targets = data.get("target", {})
        if isinstance(targets, dict):
            for target_spec, target_data in targets.items():
                if not isinstance(target_data, dict):
                    continue
                for section, dep_type in section_map.items():
                    deps = target_data.get(section, {})
                    if not isinstance(deps, dict):
                        continue
                    for name, spec in deps.items():
                        pkg = self._parse_dependency(name, spec, dep_type, file_path, f"target.{target_spec}.{section}")
                        if pkg:
                            packages.append(pkg)

        return packages

    def _parse_dependency(self, name: str, spec, dep_type: str, file_path: str, section: str) -> ParsedPackage | None:
        """Parse a single dependency entry.

        Handles:
        - String: "1.0" or "^1.0" or ">=1.0, <2.0"
        - Dict/table: { version = "1.0", features = [...], optional = true }
        - Workspace: { workspace = true }
        - Git: { git = "...", branch = "..." }
        - Path: { path = "../local" }
        """
        version = None
        version_raw = None
        version_confidence = "unknown"

        if isinstance(spec, str):
            version_raw = spec
            version, version_confidence = self._parse_version_spec(spec)
        elif isinstance(spec, dict):
            # Check for workspace dependency
            if spec.get("workspace"):
                version_confidence = "unknown"
                version_raw = "workspace"
            elif spec.get("git"):
                version_confidence = "unknown"
                version_raw = f"git:{spec['git']}"
            elif spec.get("path"):
                version_confidence = "unknown"
                version_raw = f"path:{spec['path']}"
            elif "version" in spec:
                version_raw = spec["version"]
                version, version_confidence = self._parse_version_spec(spec["version"])

            # Optional dependencies
            if spec.get("optional"):
                dep_type = "optional"
        else:
            return None

        return ParsedPackage(
            name=name,
            version=version,
            version_raw=version_raw,
            dependency_type=dep_type,
            source_file=file_path,
            source_location=f"{section}.{name}",
            version_confidence=version_confidence,
            ecosystem="cargo",
        )

    @staticmethod
    def _parse_version_spec(spec: str) -> tuple[str | None, str]:
        """Parse a Cargo version specifier.

        Returns:
            (resolved_version, confidence)
        """
        spec = spec.strip()

        # Exact version: "=1.0.0" or "1.0.0" (without prefix operators)
        if spec.startswith("="):
            return spec[1:].strip(), "exact"

        # Check for range operators
        if any(c in spec for c in ("^", "~", ">", "<", "*", ",")):
            # These are all ranges — extract the base version for querying
            # but mark as declared_range
            clean = spec.lstrip("^~>=<! ")
            if "," in clean:
                clean = clean.split(",")[0].strip().lstrip("^~>=<! ")
            return clean if clean else None, "declared_range"

        # Plain version like "1.0.0" — in Cargo this means "^1.0.0" implicitly
        # but it's the closest we have to an exact version for querying
        if spec and spec[0].isdigit():
            return spec, "declared_range"

        return None, "unknown"

    def parse_cargo_lock(self, content: str, file_path: str) -> tuple[list[ParsedPackage], list[ParsedRelationship]]:
        """Parse Cargo.lock and return exact packages and relationships."""
        try:
            data = toml.loads(content)
        except Exception:
            return [], []

        packages = []
        relationships = []

        raw_packages = data.get("package") or data.get("packages") or []
        if not isinstance(raw_packages, list):
            return [], []

        for item in raw_packages:
            if not isinstance(item, dict):
                continue

            name = item.get("name")
            version = item.get("version")
            if not name or not version:
                continue

            pkg = ParsedPackage(
                name=name,
                version=version,
                version_raw=version,
                dependency_type="transitive",
                source_file=file_path,
                source_location=f"[[package]].{name}",
                version_confidence="exact",
                ecosystem="cargo",
            )
            packages.append(pkg)

            # Dependencies
            deps = item.get("dependencies", [])
            if isinstance(deps, list):
                for dep in deps:
                    if isinstance(dep, str):
                        # dep can be formatted as "crate-name" or "crate-name 1.0.0 (registry+...)"
                        dep_name = dep.split()[0].strip()
                        relationships.append(
                            ParsedRelationship(
                                source_name=name,
                                target_name=dep_name,
                                source_file=file_path,
                                evidence_method="observed-lockfile-edge",
                                confidence="high",
                            )
                        )

        return packages, relationships

    def merge_manifest_with_lockfile(
        self,
        manifest_packages: list[ParsedPackage],
        lockfile_packages: list[ParsedPackage],
        lockfile_relationships: list[ParsedRelationship],
    ) -> tuple[list[ParsedPackage], list[ParsedRelationship]]:
        """Merge declared packages from Cargo.toml with exact packages from Cargo.lock."""
        merged_packages = {}
        for pkg in lockfile_packages:
            merged_packages[pkg.name] = pkg

        for pkg in manifest_packages:
            if pkg.name in merged_packages:
                merged_packages[pkg.name].dependency_type = pkg.dependency_type
            else:
                merged_packages[pkg.name] = pkg

        return list(merged_packages.values()), list(lockfile_relationships)
