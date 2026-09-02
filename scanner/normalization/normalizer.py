import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from scanner.parsers.base import ParsedDependency


@dataclass
class NormalizedComponent:
    """
    Standardized SBOM component representation following Package URL (PURL)
    and CycloneDX component standards with full provenance.
    """
    name: str
    version: Optional[str] = None
    raw_specifier: Optional[str] = None
    ecosystem: str = "unknown"  # pypi, npm, cargo, golang
    direct: bool = True
    source_file: str = ""
    source_files: List[str] = field(default_factory=list)
    purl: str = ""
    scope: str = "required"  # required, dev, optional, transitive
    license: Optional[str] = None
    integrity: Optional[str] = None
    resolved_url: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)  # list of child component names or purls
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version or "",
            "raw_specifier": self.raw_specifier or "",
            "ecosystem": self.ecosystem,
            "direct": self.direct,
            "source_file": self.source_file,
            "source_files": self.source_files or ([self.source_file] if self.source_file else []),
            "purl": self.purl,
            "scope": self.scope,
            "license": self.license or "",
            "integrity": self.integrity or "",
            "resolved_url": self.resolved_url or "",
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }


class DependencyNormalizer:
    """
    Normalizes parsed dependencies across ecosystems into standardized PURLs,
    canonical names, and deduplicated component models.
    """

    @staticmethod
    def normalize_name(name: str, ecosystem: str) -> str:
        clean = name.strip()
        eco = ecosystem.lower()
        if eco == "pypi":
            # PEP 503 normalization: lower-case, replace run of [-_.] with single '-'
            return re.sub(r"[-_.]+", "-", clean).lower()
        elif eco == "npm" or eco == "cargo":
            return clean.lower()
        elif eco == "golang":
            return clean
        return clean

    @classmethod
    def generate_purl(cls, name: str, version: Optional[str], ecosystem: str) -> str:
        """
        Generates standard Package URL (PURL) according to https://github.com/package-url/purl-spec
        """
        eco = ecosystem.lower()
        if eco == "pypi":
            norm_name = cls.normalize_name(name, "pypi")
            if version:
                return f"pkg:pypi/{norm_name}@{version}"
            return f"pkg:pypi/{norm_name}"
        elif eco == "npm":
            norm_name = name.strip()
            # Handle scoped packages @scope/package -> pkg:npm/%40scope/package@version or @scope/package
            if norm_name.startswith("@") and "/" in norm_name:
                scope, pkg = norm_name.split("/", 1)
                encoded_scope = quote(scope)
                if version:
                    return f"pkg:npm/{encoded_scope}/{pkg}@{version}"
                return f"pkg:npm/{encoded_scope}/{pkg}"
            else:
                norm_name = norm_name.lower()
                if version:
                    return f"pkg:npm/{norm_name}@{version}"
                return f"pkg:npm/{norm_name}"
        elif eco == "cargo":
            norm_name = cls.normalize_name(name, "cargo")
            if version:
                return f"pkg:cargo/{norm_name}@{version}"
            return f"pkg:cargo/{norm_name}"
        elif eco == "golang":
            norm_name = name.strip()
            if version:
                return f"pkg:golang/{norm_name}@{version}"
            return f"pkg:golang/{norm_name}"
        else:
            if version:
                return f"pkg:generic/{name}@{version}"
            return f"pkg:generic/{name}"

    @classmethod
    def normalize_list(cls, parsed_deps: List[ParsedDependency]) -> List[NormalizedComponent]:
        """
        Normalizes a list of parsed dependencies and merges entries for the same package
        (e.g., combining manifest specification with lockfile resolution).
        """
        components_map: Dict[str, NormalizedComponent] = {}

        for dep in parsed_deps:
            eco = dep.ecosystem.lower()
            canonical_name = cls.normalize_name(dep.name, eco)
            key = f"{eco}:{canonical_name}"

            if key not in components_map:
                purl = cls.generate_purl(canonical_name, dep.version, eco)
                comp = NormalizedComponent(
                    name=canonical_name,
                    version=dep.version,
                    raw_specifier=dep.specifier,
                    ecosystem=eco,
                    direct=dep.direct,
                    source_file=dep.source_file,
                    source_files=[dep.source_file] if dep.source_file else [],
                    purl=purl,
                    scope=dep.scope,
                    license=dep.license,
                    integrity=dep.integrity,
                    resolved_url=dep.resolved_url,
                    dependencies=list(dep.dependencies),
                    metadata=dict(dep.metadata),
                )
                components_map[key] = comp
            else:
                existing = components_map[key]
                # Merge logic:
                # 1. Direct status: if either marks direct, it is direct
                if dep.direct:
                    existing.direct = True

                # 2. Version: prioritize locked/exact version over None or range specifier
                if not existing.version and dep.version:
                    existing.version = dep.version
                    existing.purl = cls.generate_purl(canonical_name, dep.version, eco)
                elif existing.version and dep.version and existing.version != dep.version:
                    if existing.raw_specifier and not dep.specifier:
                        # existing had a specifier, dep might have exact version from lockfile
                        existing.version = dep.version
                        existing.purl = cls.generate_purl(canonical_name, dep.version, eco)

                # 3. Source files tracking
                if dep.source_file and dep.source_file not in existing.source_files:
                    existing.source_files.append(dep.source_file)
                    if not existing.source_file:
                        existing.source_file = dep.source_file

                # 4. Integrity & metadata
                if dep.integrity and not existing.integrity:
                    existing.integrity = dep.integrity
                if dep.resolved_url and not existing.resolved_url:
                    existing.resolved_url = dep.resolved_url
                if dep.license and not existing.license:
                    existing.license = dep.license
                if dep.dependencies:
                    for d in dep.dependencies:
                        if d not in existing.dependencies:
                            existing.dependencies.append(d)
                if dep.metadata:
                    existing.metadata.update(dep.metadata)

        return list(components_map.values())
