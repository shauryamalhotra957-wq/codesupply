"""Maven POM XML parser."""

import xml.etree.ElementTree as ET

from app.services.normalizer import ParsedPackage

# Map Maven scopes to dependency types
_SCOPE_MAP = {
    "compile": "direct",
    "runtime": "direct",
    "provided": "direct",
    "system": "direct",
    "test": "dev",
    "import": "direct",
}


class MavenParser:
    """Parses pom.xml files to extract dependency declarations.

    Supports:
    - Standard dependency extraction (groupId, artifactId, version, scope)
    - Property resolution (${property.name})
    - Maven namespace handling
    - Missing version/scope defaults
    """

    def parse_pom_xml(self, content: str, file_path: str) -> list[ParsedPackage]:
        """Parse pom.xml and extract dependencies."""
        packages = []

        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            return []

        # Handle Maven namespace
        ns = ""
        if root.tag.startswith("{"):
            ns = root.tag.split("}")[0] + "}"

        # Extract properties for variable resolution
        properties = self._extract_properties(root, ns)

        # Find all dependency elements
        dependencies = root.findall(f".//{ns}dependencies/{ns}dependency")

        for i, dep in enumerate(dependencies):
            group_id_elem = dep.find(f"{ns}groupId")
            artifact_id_elem = dep.find(f"{ns}artifactId")
            version_elem = dep.find(f"{ns}version")
            scope_elem = dep.find(f"{ns}scope")

            if group_id_elem is None or artifact_id_elem is None:
                continue

            group_id = (group_id_elem.text or "").strip()
            artifact_id = (artifact_id_elem.text or "").strip()

            if not group_id or not artifact_id:
                continue

            # Resolve version (may be a property reference)
            raw_version = (version_elem.text or "").strip() if version_elem is not None else None
            version, version_confidence = self._resolve_version(raw_version, properties)

            # Map scope to dependency type
            scope = (scope_elem.text or "compile").strip().lower() if scope_elem is not None else "compile"
            dep_type = _SCOPE_MAP.get(scope, "direct")

            name = f"{group_id}:{artifact_id}"

            pkg = ParsedPackage(
                name=name,
                version=version,
                version_raw=raw_version,
                dependency_type=dep_type,
                source_file=file_path,
                source_location=f"dependencies/dependency[{i}]",
                version_confidence=version_confidence,
                ecosystem="maven",
                package_manager="maven",
            )
            packages.append(pkg)

        return packages

    def _extract_properties(self, root: ET.Element, ns: str) -> dict[str, str]:
        """Extract <properties> from pom.xml for variable resolution."""
        properties: dict[str, str] = {}
        props_elem = root.find(f"{ns}properties")
        if props_elem is not None:
            for child in props_elem:
                tag = child.tag
                if ns and tag.startswith(ns):
                    tag = tag[len(ns) :]
                if child.text:
                    properties[tag] = child.text.strip()
        return properties

    def _resolve_version(self, raw_version: str | None, properties: dict[str, str]) -> tuple[str | None, str]:
        """Resolve a version string, handling Maven property references.

        Returns:
            (resolved_version, version_confidence)
        """
        if not raw_version:
            return None, "unknown"

        # Property reference: ${property.name}
        if raw_version.startswith("${") and raw_version.endswith("}"):
            prop_name = raw_version[2:-1]
            resolved = properties.get(prop_name)
            if resolved:
                # Check if resolved value is itself a version range
                if any(c in resolved for c in "[]()"):
                    return resolved, "declared_range"
                return resolved, "exact"
            else:
                return None, "unknown"

        # Version ranges: [1.0,2.0), (,1.0], etc.
        if any(c in raw_version for c in "[]()"):
            return raw_version, "declared_range"

        # Plain version number
        return raw_version, "exact"
