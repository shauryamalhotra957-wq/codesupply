"""Component normalization and Package URL generation."""

import re
import uuid
from dataclasses import dataclass

from packageurl import PackageURL


@dataclass
class ParsedPackage:
    """Intermediate representation of a parsed package from any ecosystem."""

    name: str
    version: str | None
    version_raw: str | None
    dependency_type: str  # direct, dev, transitive, optional, peer, unknown
    source_file: str
    source_location: str | None
    version_confidence: str  # exact, declared_range, inferred, unknown
    ecosystem: str = "npm"
    package_manager: str | None = None
    integrity: str | None = None
    resolved_url: str | None = None
    dependencies: list[str] | None = None
    license: str | None = None


@dataclass
class ParsedRelationship:
    """Intermediate representation of a parsed dependency relationship."""

    source_name: str
    target_name: str
    source_file: str
    evidence_method: str  # declared, observed-lockfile-edge, inferred
    confidence: str  # high, medium, low


class ComponentNormalizer:
    """Normalizes parsed packages into a common component representation."""

    def normalize(self, parsed: ParsedPackage, scan_id: str) -> tuple[dict, list[dict]]:
        """Convert ParsedPackage to normalized component dict + evidence dicts.

        Returns:
            (component_dict, list_of_evidence_dicts)
        """
        comp_id = uuid.uuid4().hex
        normalized_name = self._normalize_name(parsed.ecosystem, parsed.name)

        # Map dependency types to standard values
        dep_type = parsed.dependency_type
        if dep_type in ("dev", "peer", "optional"):
            dep_type = "direct"  # These are all direct declarations from different sections

        purl = self.generate_purl(parsed.ecosystem, parsed.name, parsed.version)

        component = {
            "id": comp_id,
            "name": parsed.name,
            "version": parsed.version,
            "ecosystem": parsed.ecosystem,
            "package_manager": parsed.package_manager or parsed.ecosystem,
            "dependency_type": dep_type,
            "source_file": parsed.source_file,
            "source_location": parsed.source_location,
            "version_confidence": parsed.version_confidence,
            "purl": purl,
            "original_declaration": parsed.version_raw,
            "normalized_name": normalized_name,
            "license": parsed.license,
        }

        evidences = []

        # Version evidence
        if parsed.version:
            method = (
                "lockfile-resolution"
                if parsed.version_confidence == "exact" and "lock" in parsed.source_file
                else "declared-range"
            )
            if parsed.version_confidence == "exact":
                method = "lockfile-resolution" if "lock" in parsed.source_file.lower() else "declared"

            evidences.append(
                {
                    "source_file": parsed.source_file,
                    "source_location": parsed.source_location,
                    "method": method,
                    "confidence": parsed.version_confidence,
                    "value": parsed.version,
                    "evidence_type": "version",
                }
            )
        elif parsed.version_raw:
            evidences.append(
                {
                    "source_file": parsed.source_file,
                    "source_location": parsed.source_location,
                    "method": "declared-range",
                    "confidence": parsed.version_confidence,
                    "value": parsed.version_raw,
                    "evidence_type": "version",
                }
            )

        # Dependency type evidence
        evidences.append(
            {
                "source_file": parsed.source_file,
                "source_location": parsed.source_location,
                "method": "declared",
                "confidence": "exact" if dep_type in ("direct", "transitive") else "inferred",
                "value": dep_type,
                "evidence_type": "dependency_type",
            }
        )

        return component, evidences

    def _normalize_name(self, ecosystem: str, name: str) -> str:
        """Normalize package name per ecosystem conventions."""
        if ecosystem == "pypi":
            # PEP 503: lowercase, replace [-_.] runs with single hyphen
            return re.sub(r"[-_.]+", "-", name).lower()
        elif ecosystem == "npm":
            return name.lower()
        elif ecosystem == "maven":
            # Maven: preserve case as groupId:artifactId is case-sensitive
            return name
        elif ecosystem in ("golang", "cargo"):
            # Go modules and Rust crates: case-sensitive
            return name
        return name.lower()

    def generate_purl(self, ecosystem: str, name: str, version: str | None) -> str | None:
        """Generate Package URL according to the purl spec."""
        if not name:
            return None

        try:
            purl_type = ecosystem.lower()
            namespace = None
            pkg_name = name

            if purl_type == "npm":
                # Handle scoped npm packages (@org/pkg)
                if name.startswith("@"):
                    parts = name.split("/", 1)
                    if len(parts) == 2:
                        namespace = parts[0][1:]  # remove @
                        pkg_name = parts[1]

            elif purl_type == "pypi":
                # PEP 503 normalization
                pkg_name = re.sub(r"[-_.]+", "-", name).lower()

            elif purl_type == "maven":
                # Maven: name is groupId:artifactId
                if ":" in name:
                    parts = name.split(":", 1)
                    namespace = parts[0]
                    pkg_name = parts[1]

            elif purl_type == "golang":
                # Go modules: github.com/org/repo → namespace=github.com/org, name=repo
                if "/" in name:
                    last_slash = name.rfind("/")
                    namespace = name[:last_slash]
                    pkg_name = name[last_slash + 1 :]

            elif purl_type == "cargo":
                # Rust crates: flat namespace
                pass  # no namespace needed

            return str(
                PackageURL(
                    type=purl_type,
                    namespace=namespace,
                    name=pkg_name,
                    version=version,
                )
            )
        except Exception:
            return None
