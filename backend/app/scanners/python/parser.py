import toml
from packaging.requirements import InvalidRequirement, Requirement

from app.services.normalizer import ParsedPackage


class PythonParser:
    def parse_requirements_txt(self, content: str, file_path: str) -> list[ParsedPackage]:
        packages = []
        lines = content.splitlines()

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):  # Skip comments and flags
                continue

            try:
                # Handle inline comments
                req_str = line.split("#")[0].strip()
                req = Requirement(req_str)

                version = None
                version_confidence = "unknown"
                version_raw_str = str(req.specifier) if req.specifier else None

                if req.specifier:
                    version_confidence = "declared_range"
                    # Try to find exact version
                    for spec in req.specifier:
                        if spec.operator == "==":
                            version = spec.version
                            version_confidence = "exact"
                            break

                pkg = ParsedPackage(
                    name=req.name,
                    version=version,
                    version_raw=version_raw_str,
                    dependency_type="direct",
                    source_file=file_path,
                    source_location=f"line {i + 1}",
                    version_confidence=version_confidence,
                    ecosystem="pypi",
                )
                packages.append(pkg)
            except InvalidRequirement:
                continue

        return packages

    def parse_pyproject_toml(self, content: str, file_path: str) -> list[ParsedPackage]:
        try:
            data = toml.loads(content)
        except Exception:
            return []

        packages = []

        # Parse [project.dependencies]
        deps = data.get("project", {}).get("dependencies", [])
        for i, dep_str in enumerate(deps):
            try:
                req = Requirement(dep_str)
                version = None
                version_confidence = "declared_range"

                for spec in req.specifier:
                    if spec.operator == "==":
                        version = spec.version
                        version_confidence = "exact"
                        break

                pkg = ParsedPackage(
                    name=req.name,
                    version=version,
                    version_raw=str(req.specifier) if req.specifier else None,
                    dependency_type="direct",
                    source_file=file_path,
                    source_location=f"project.dependencies[{i}]",
                    version_confidence=version_confidence,
                    ecosystem="pypi",
                )
                packages.append(pkg)
            except InvalidRequirement:
                continue

        # Parse [project.optional-dependencies]
        opt_deps = data.get("project", {}).get("optional-dependencies", {})
        for extra, deps_list in opt_deps.items():
            for i, dep_str in enumerate(deps_list):
                try:
                    req = Requirement(dep_str)
                    version = None
                    version_confidence = "declared_range"

                    for spec in req.specifier:
                        if spec.operator == "==":
                            version = spec.version
                            version_confidence = "exact"
                            break

                    pkg = ParsedPackage(
                        name=req.name,
                        version=version,
                        version_raw=str(req.specifier) if req.specifier else None,
                        dependency_type="optional",
                        source_file=file_path,
                        source_location=f"project.optional-dependencies.{extra}[{i}]",
                        version_confidence=version_confidence,
                        ecosystem="pypi",
                    )
                    packages.append(pkg)
                except InvalidRequirement:
                    continue

        return packages
