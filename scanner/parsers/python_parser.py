import re
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

from scanner.parsers.base import BaseParser, ParsedDependency

# Regex for PEP 508 / requirements.txt requirement lines
# Matches package_name[extras] specifiers ; markers
REQ_PATTERN = re.compile(
    r"^([a-zA-Z0-9_\-\.]+)(?:\[([a-zA-Z0-9_\-,\s]+)\])?\s*([=><~^!].*?)?(?:\s*;\s*(.*))?$"
)


class PythonParser(BaseParser):
    """
    Parses Python requirements.txt and pyproject.toml files.
    Extracts package names, versions, specifiers, extras, and markers.
    """

    def can_parse(self, filename: str) -> bool:
        lower = filename.lower()
        return (
            lower == "requirements.txt"
            or (lower.startswith("requirements") and lower.endswith(".txt"))
            or lower == "pyproject.toml"
        )

    def parse(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        filename = file_path.name.lower()
        if filename.endswith(".txt"):
            return self._parse_requirements_txt(file_path, relative_path)
        elif filename == "pyproject.toml":
            return self._parse_pyproject_toml(file_path, relative_path)
        return []

    def _parse_requirements_line(self, line: str, source_file: str) -> Optional[ParsedDependency]:
        clean = line.strip()
        if not clean or clean.startswith("#"):
            return None

        # Ignore pip flags (-r other.txt, -i url, -e ., --index-url, etc.)
        if clean.startswith(("-r", "-i", "-f", "-e", "--", "-c", "--extra-index-url")):
            # If -e was used with a git or path url, we record it if possible or ignore
            if clean.startswith("-e "):
                clean = clean[3:].strip()
            else:
                return None

        # Strip inline comments (outside quotes)
        if " #" in clean:
            clean = clean.split(" #")[0].strip()

        # Check for URL-based or git packages: git+https://github.com/.../pkg.git@v1.0#egg=pkg
        if "#egg=" in clean:
            match = re.search(r"#egg=([a-zA-Z0-9_\-\.]+)", clean)
            if match:
                pkg_name = match.group(1)
                return ParsedDependency(
                    name=pkg_name,
                    version=None,
                    specifier=clean,
                    ecosystem="pypi",
                    direct=True,
                    source_file=source_file,
                    scope="required",
                    metadata={"url_install": clean},
                )

        match = REQ_PATTERN.match(clean)
        if not match:
            # Fallback simple word match if line is just package name without specifier
            word_match = re.match(r"^([a-zA-Z0-9_\-\.]+)", clean)
            if word_match:
                pkg_name = word_match.group(1)
                return ParsedDependency(
                    name=pkg_name,
                    version=None,
                    specifier="",
                    ecosystem="pypi",
                    direct=True,
                    source_file=source_file,
                    scope="required",
                )
            return None

        name = match.group(1)
        extras = match.group(2)
        raw_spec = (match.group(3) or "").strip()
        marker = (match.group(4) or "").strip()

        version, clean_spec = self._extract_version_from_specifier(raw_spec)

        metadata = {}
        if extras:
            metadata["extras"] = [e.strip() for e in extras.split(",")]
        if marker:
            metadata["marker"] = marker

        return ParsedDependency(
            name=name,
            version=version,
            specifier=clean_spec if clean_spec else raw_spec,
            ecosystem="pypi",
            direct=True,
            source_file=source_file,
            scope="required",
            metadata=metadata,
        )

    def _extract_version_from_specifier(self, spec: str) -> Tuple[Optional[str], str]:
        """
        Extracts exact pinned version (from ==, ===, ~=) or returns None if range.
        """
        if not spec:
            return None, ""

        # Exact pinned: ==2.31.0 or ===2.31.0
        exact_match = re.match(r"^={2,3}\s*([0-9a-zA-Z_\.\-+]+)$", spec)
        if exact_match:
            return exact_match.group(1), spec

        # Compatible release ~=2.31.0 -> specifier preserved
        compatible_match = re.match(r"^~=\s*([0-9a-zA-Z_\.\-+]+)$", spec)
        if compatible_match:
            # For compatible release, base version is the minimum
            return compatible_match.group(1), spec

        # First match if compound (e.g. >=1.2.0, <2.0.0)
        return None, spec

    def _parse_requirements_txt(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        dependencies: List[ParsedDependency] = []
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                dep = self._parse_requirements_line(line, relative_path)
                if dep:
                    dependencies.append(dep)
        except Exception:
            pass
        return dependencies

    def _parse_pyproject_toml(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        dependencies: List[ParsedDependency] = []
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            if tomllib:
                data = tomllib.loads(content)
            else:
                data = self._basic_toml_parse(content)

            # 1. Standard PEP 621: project.dependencies
            project = data.get("project", {})
            if isinstance(project, dict):
                standard_deps = project.get("dependencies", [])
                if isinstance(standard_deps, list):
                    for req in standard_deps:
                        if isinstance(req, str):
                            dep = self._parse_requirements_line(req, relative_path)
                            if dep:
                                dependencies.append(dep)

                # Optional dependencies
                opt_deps = project.get("optional-dependencies", {})
                if isinstance(opt_deps, dict):
                    for group_name, group_list in opt_deps.items():
                        if isinstance(group_list, list):
                            for req in group_list:
                                if isinstance(req, str):
                                    dep = self._parse_requirements_line(req, relative_path)
                                    if dep:
                                        dep.scope = "optional"
                                        dep.metadata["group"] = group_name
                                        dependencies.append(dep)

            # 2. Poetry: tool.poetry.dependencies
            tool = data.get("tool", {})
            if isinstance(tool, dict):
                poetry = tool.get("poetry", {})
                if isinstance(poetry, dict):
                    poetry_deps = poetry.get("dependencies", {})
                    if isinstance(poetry_deps, dict):
                        for name, spec in poetry_deps.items():
                            if name.lower() == "python":
                                continue  # Python runtime constraint
                            if isinstance(spec, str):
                                version, clean_spec = self._extract_version_from_specifier(spec)
                                # If poetry version uses ^ or ~ or exact number
                                if not version and re.match(r"^[0-9]", spec):
                                    version = spec
                                dependencies.append(
                                    ParsedDependency(
                                        name=name,
                                        version=version,
                                        specifier=spec,
                                        ecosystem="pypi",
                                        direct=True,
                                        source_file=relative_path,
                                        scope="required",
                                    )
                                )
                            elif isinstance(spec, dict):
                                v_str = str(spec.get("version", ""))
                                version, clean_spec = self._extract_version_from_specifier(v_str)
                                dependencies.append(
                                    ParsedDependency(
                                        name=name,
                                        version=version or (v_str if re.match(r"^[0-9]", v_str) else None),
                                        specifier=v_str,
                                        ecosystem="pypi",
                                        direct=True,
                                        source_file=relative_path,
                                        scope="optional" if spec.get("optional") else "required",
                                        metadata={"poetry_spec": spec},
                                    )
                                )
        except Exception:
            pass
        return dependencies

    def _basic_toml_parse(self, content: str) -> dict:
        """Fallback lightweight TOML parser for basic key-value tables when tomllib is missing."""
        result: dict = {}
        current_table = result
        current_section = ""

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            sec_match = re.match(r"^\[([a-zA-Z0-9_\-\.]+)\]$", line)
            if sec_match:
                section_path = sec_match.group(1).split(".")
                current_table = result
                for part in section_path:
                    current_table = current_table.setdefault(part, {})
                continue

            # Key-value assignment: key = "value"
            kv_match = re.match(r"^([a-zA-Z0-9_\-\.]+)\s*=\s*(.*)$", line)
            if kv_match:
                key, val = kv_match.group(1), kv_match.group(2).strip()
                # Clean quotes
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                current_table[key] = val

        return result
