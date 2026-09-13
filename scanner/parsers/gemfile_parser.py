import re
from pathlib import Path
from typing import List, Optional

from scanner.parsers.base import BaseParser, ParsedDependency


class GemfileParser(BaseParser):
    """
    Parses Ruby Gemfile and Gemfile.lock files.
    Extracts direct and transitive gem dependencies, versions, and dependencies.
    """

    def can_parse(self, filename: str) -> bool:
        lower = filename.lower()
        return (
            lower == "gemfile"
            or lower.endswith("gemfile")
            or lower == "gemfile.lock"
            or lower.endswith("gemfile.lock")
        )

    def parse(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        filename = file_path.name.lower()
        if filename == "gemfile.lock" or filename.endswith("gemfile.lock"):
            return self._parse_gemfile_lock(file_path, relative_path)
        elif filename == "gemfile" or filename.endswith("gemfile"):
            return self._parse_gemfile(file_path, relative_path)
        return []

    def _parse_gemfile(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        """Parses direct dependencies from a Ruby Gemfile."""
        deps: List[ParsedDependency] = []
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return deps

        gem_pattern = re.compile(
            r"""gem\s+['"]([a-zA-Z0-9_\-\.]+)['"](?:\s*,\s*['"]([^'"]+)['"])?"""
        )
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("#"):
                continue
            match = gem_pattern.search(line)
            if match:
                name = match.group(1)
                specifier = match.group(2) if match.group(2) else None
                version = None
                if specifier and re.match(r"^\d+(\.\d+)*", specifier):
                    version = specifier
                deps.append(
                    ParsedDependency(
                        name=name,
                        version=version,
                        specifier=specifier,
                        ecosystem="gem",
                        direct=True,
                        source_file=relative_path,
                        scope="required",
                    )
                )
        return deps

    def _parse_gemfile_lock(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        """Parses dependencies from a Gemfile.lock."""
        deps: List[ParsedDependency] = []
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return deps

        lines = content.splitlines()
        section = None
        current_dep: Optional[ParsedDependency] = None

        direct_dependencies = set()

        # First pass to find direct dependencies declared in DEPENDENCIES section
        dep_section = False
        for line in lines:
            stripped = line.strip()
            if stripped in ("GEM", "PLATFORMS", "DEPENDENCIES", "BUNDLED WITH", "GIT", "PATH"):
                dep_section = (stripped == "DEPENDENCIES")
                continue
            if dep_section and stripped:
                match = re.match(r"^([a-zA-Z0-9_\-\.]+)(?:\s*\((.+)\))?", stripped)
                if match:
                    direct_dependencies.add(match.group(1))

        # Second pass to parse GEM specs
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped in ("GEM", "PLATFORMS", "DEPENDENCIES", "BUNDLED WITH", "GIT", "PATH"):
                section = stripped
                current_dep = None
                continue

            if section == "GEM":
                # Package header line: 4 spaces indent, e.g., "    rails (7.1.3.2)"
                if line.startswith("    ") and not line.startswith("      "):
                    spec_match = re.match(r"^([a-zA-Z0-9_\-\.]+)\s+\((.+)\)", stripped)
                    if spec_match:
                        name = spec_match.group(1)
                        version = spec_match.group(2)
                        is_direct = name in direct_dependencies
                        current_dep = ParsedDependency(
                            name=name,
                            version=version,
                            specifier=f"=={version}",
                            ecosystem="gem",
                            direct=is_direct,
                            source_file=relative_path,
                            scope="required" if is_direct else "transitive",
                        )
                        deps.append(current_dep)
                # Child dependency line: 6 spaces indent, e.g., "      actionpack (= 7.1.3.2)"
                elif line.startswith("      ") and current_dep is not None:
                    child_match = re.match(r"^([a-zA-Z0-9_\-\.]+)", stripped)
                    if child_match:
                        current_dep.dependencies.append(child_match.group(1))

        return deps
