"""Rust Cargo.toml parser — parses Cargo manifest files."""

import toml

from app.services.normalizer import ParsedPackage


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
