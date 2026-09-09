"""Go module parser — parses go.mod files."""

import re

from app.services.normalizer import ParsedPackage, ParsedRelationship


class GoParser:
    """Parses go.mod files to extract module dependencies.

    Supports:
    - module directive (project identity)
    - Single-line and grouped require directives
    - // indirect comment classification
    - replace directives (version override)
    """

    def parse_go_mod(self, content: str, file_path: str) -> tuple[list[ParsedPackage], list[ParsedRelationship]]:
        """Parse go.mod and return packages and relationships."""
        packages = []
        relationships = []

        lines = content.splitlines()
        module_name = None
        in_require_block = False
        in_replace_block = False
        replaces: dict[str, str] = {}  # module -> replacement version
        line_num = 0

        for line in lines:
            line_num += 1
            stripped = line.strip()

            # Skip empty lines and pure comments
            if not stripped or stripped.startswith("//"):
                continue

            # Module directive
            if stripped.startswith("module "):
                module_name = stripped.split(None, 1)[1].strip()
                continue

            # Block starts
            if stripped.startswith("require ("):
                in_require_block = True
                continue
            if stripped.startswith("replace ("):
                in_replace_block = True
                continue

            # Block ends
            if stripped == ")":
                in_require_block = False
                in_replace_block = False
                continue

            # Single-line require
            if stripped.startswith("require ") and not in_require_block:
                dep_str = stripped[len("require ") :].strip()
                pkg = self._parse_require_line(dep_str, file_path, line_num)
                if pkg:
                    packages.append(pkg)
                    if module_name:
                        relationships.append(
                            ParsedRelationship(
                                source_name=module_name,
                                target_name=pkg.name,
                                source_file=file_path,
                                evidence_method="declared",
                                confidence="high",
                            )
                        )
                continue

            # Inside require block
            if in_require_block:
                pkg = self._parse_require_line(stripped, file_path, line_num)
                if pkg:
                    packages.append(pkg)
                    if module_name:
                        relationships.append(
                            ParsedRelationship(
                                source_name=module_name,
                                target_name=pkg.name,
                                source_file=file_path,
                                evidence_method="declared",
                                confidence="high",
                            )
                        )
                continue

            # Inside replace block
            if in_replace_block:
                match = re.match(r"^(\S+)(?:\s+\S+)?\s+=>\s+\S+\s+(\S+)", stripped)
                if match:
                    v = match.group(2).lstrip("v")
                    replaces[match.group(1)] = v
                continue

            # Single-line replace
            if stripped.startswith("replace "):
                replace_str = stripped[len("replace ") :].strip()
                match = re.match(r"^(\S+)(?:\s+\S+)?\s+=>\s+\S+\s+(\S+)", replace_str)
                if match:
                    v = match.group(2).lstrip("v")
                    replaces[match.group(1)] = v

        # Apply replace directives
        for pkg in packages:
            if pkg.name in replaces:
                pkg.version = replaces[pkg.name]
                pkg.version_raw = replaces[pkg.name]
                pkg.version_confidence = "exact"

        return packages, relationships

    def _parse_require_line(self, line: str, file_path: str, line_num: int) -> ParsedPackage | None:
        """Parse a single require line like 'github.com/gin-gonic/gin v1.9.1 // indirect'."""
        # Remove inline comments but check for // indirect first
        is_indirect = "// indirect" in line
        line_clean = re.sub(r"//.*$", "", line).strip()

        parts = line_clean.split()
        if len(parts) < 2:
            return None

        name = parts[0]
        version_raw = parts[1]

        # Go versions start with 'v'
        version = version_raw.lstrip("v") if version_raw.startswith("v") else version_raw

        return ParsedPackage(
            name=name,
            version=version,
            version_raw=version_raw,
            dependency_type="transitive" if is_indirect else "direct",
            source_file=file_path,
            source_location=f"line {line_num}",
            version_confidence="exact",
            ecosystem="golang",
        )
