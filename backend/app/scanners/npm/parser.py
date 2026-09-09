import json

from app.services.normalizer import ParsedPackage, ParsedRelationship


class NpmParser:
    def parse_package_json(self, content: str, file_path: str) -> tuple[list[ParsedPackage], list[ParsedRelationship]]:
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return [], []

        packages = []
        relationships = []

        project_name = data.get("name", "unknown-project")

        dep_types = {
            "dependencies": "direct",
            "devDependencies": "dev",
            "peerDependencies": "peer",
            "optionalDependencies": "optional",
        }

        import re

        semver_exact_regex = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$")

        for section, dep_type in dep_types.items():
            deps = data.get(section, {})
            if not isinstance(deps, dict):
                continue

            for name, version in deps.items():
                if not isinstance(version, str):
                    continue

                pkg = ParsedPackage(
                    name=name,
                    version=None,  # Only known exactly from lockfile normally, or if it's exact in package.json
                    version_raw=version,
                    dependency_type=dep_type,
                    source_file=file_path,
                    source_location=f"$.{section}.{name}",
                    version_confidence="declared_range",
                    ecosystem="npm",
                )

                # Check if exact semver version (e.g. 1.2.3 or 1.2.3-beta.1)
                v_clean = version.strip()
                if semver_exact_regex.match(v_clean):
                    pkg.version = v_clean
                    pkg.version_confidence = "exact"

                packages.append(pkg)

                relationships.append(
                    ParsedRelationship(
                        source_name=project_name,
                        target_name=name,
                        source_file=file_path,
                        evidence_method="declared",
                        confidence="high",
                    )
                )

        return packages, relationships

    def parse_package_lock(self, content: str, file_path: str) -> tuple[list[ParsedPackage], list[ParsedRelationship]]:
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return [], []

        packages = []
        relationships = []

        # Support lockfileVersion 2 and 3
        if "packages" in data:
            # v2/v3
            for path, info in data["packages"].items():
                if not path:  # root project
                    continue

                # path is like "node_modules/pkg" or "node_modules/parent/node_modules/pkg"
                name = info.get("name")
                if not name:
                    name = path.split("node_modules/")[-1]

                pkg = ParsedPackage(
                    name=name,
                    version=info.get("version"),
                    version_raw=info.get("version"),
                    dependency_type="transitive",  # Will be updated during merge if direct
                    source_file=file_path,
                    source_location=f"$.packages['{path}']",
                    version_confidence="exact",
                    ecosystem="npm",
                    integrity=info.get("integrity"),
                    resolved_url=info.get("resolved"),
                    license=info.get("license"),
                )

                if info.get("dev"):
                    pkg.dependency_type = "dev"

                packages.append(pkg)

                # Dependencies
                deps = info.get("dependencies", {})
                for dep_name, dep_info in deps.items():
                    relationships.append(
                        ParsedRelationship(
                            source_name=name,
                            target_name=dep_name,
                            source_file=file_path,
                            evidence_method="observed-lockfile-edge",
                            confidence="high",
                        )
                    )
        elif "dependencies" in data:
            # v1
            for name, info in data["dependencies"].items():
                pkg = ParsedPackage(
                    name=name,
                    version=info.get("version"),
                    version_raw=info.get("version"),
                    dependency_type="transitive",
                    source_file=file_path,
                    source_location=f"$.dependencies.{name}",
                    version_confidence="exact",
                    ecosystem="npm",
                    integrity=info.get("integrity"),
                    resolved_url=info.get("resolved"),
                )

                if info.get("dev"):
                    pkg.dependency_type = "dev"

                packages.append(pkg)

        return packages, relationships

    def merge_declarations_with_lockfile(
        self,
        declarations: list[ParsedPackage],
        lockfile_packages: list[ParsedPackage],
        lockfile_relationships: list[ParsedRelationship],
    ) -> tuple[list[ParsedPackage], list[ParsedRelationship]]:

        merged_packages = {}
        merged_relationships = list(lockfile_relationships)

        # Add lockfile packages first (exact versions)
        for pkg in lockfile_packages:
            merged_packages[pkg.name] = pkg

        # Update with declarations
        for pkg in declarations:
            if pkg.name in merged_packages:
                merged_packages[pkg.name].dependency_type = pkg.dependency_type
            else:
                merged_packages[pkg.name] = pkg

        return list(merged_packages.values()), merged_relationships
