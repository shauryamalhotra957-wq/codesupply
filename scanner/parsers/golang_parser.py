import re
from pathlib import Path
from typing import List, Optional

from scanner.parsers.base import BaseParser, ParsedDependency


class GolangParser(BaseParser):
    """
    Parses Go go.mod and go.sum files.
    Extracts module dependencies, semantic versions, indirect/direct flags, and checksums.
    """

    def can_parse(self, filename: str) -> bool:
        lower = filename.lower()
        return lower == "go.mod" or lower.endswith("go.mod") or lower == "go.sum" or lower.endswith("go.sum")

    def parse(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        filename = file_path.name.lower()
        if filename == "go.mod" or filename.endswith("go.mod"):
            return self._parse_go_mod(file_path, relative_path)
        elif filename == "go.sum" or filename.endswith("go.sum"):
            return self._parse_go_sum(file_path, relative_path)
        return []

    def _parse_go_mod(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        deps: List[ParsedDependency] = []
        in_require_block = False

        require_single_re = re.compile(r"^require\s+([^\s]+)\s+([^\s]+)(?:\s+//\s*(.*))?$")
        require_block_line_re = re.compile(r"^([^\s]+)\s+([^\s]+)(?:\s+//\s*(.*))?$")

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    clean = line.strip()
                    if not clean or clean.startswith("//"):
                        continue

                    if clean == "require (":
                        in_require_block = True
                        continue
                    elif clean == ")" and in_require_block:
                        in_require_block = False
                        continue

                    if in_require_block:
                        match = require_block_line_re.match(clean)
                        if match:
                            pkg_name = match.group(1)
                            version = match.group(2)
                            comment = match.group(3) or ""
                            is_indirect = "indirect" in comment.lower()

                            deps.append(
                                ParsedDependency(
                                    name=pkg_name,
                                    version=version.lstrip("v"),
                                    specifier=version,
                                    ecosystem="golang",
                                    direct=not is_indirect,
                                    source_file=relative_path,
                                    scope="required" if not is_indirect else "transitive",
                                )
                            )
                    else:
                        match = require_single_re.match(clean)
                        if match:
                            pkg_name = match.group(1)
                            version = match.group(2)
                            comment = match.group(3) or ""
                            is_indirect = "indirect" in comment.lower()

                            deps.append(
                                ParsedDependency(
                                    name=pkg_name,
                                    version=version.lstrip("v"),
                                    specifier=version,
                                    ecosystem="golang",
                                    direct=not is_indirect,
                                    source_file=relative_path,
                                    scope="required" if not is_indirect else "transitive",
                                )
                            )
        except Exception:
            pass

        return deps

    def _parse_go_sum(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        deps: List[ParsedDependency] = []
        seen = set()

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        name = parts[0]
                        version_raw = parts[1].replace("/go.mod", "")
                        hash_val = parts[2]

                        key = (name, version_raw)
                        if key in seen:
                            continue
                        seen.add(key)

                        deps.append(
                            ParsedDependency(
                                name=name,
                                version=version_raw.lstrip("v"),
                                specifier=version_raw,
                                ecosystem="golang",
                                direct=False,
                                source_file=relative_path,
                                integrity=hash_val,
                            )
                        )
        except Exception:
            pass

        return deps
