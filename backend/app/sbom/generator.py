import uuid
from datetime import datetime, timezone

from app.models.models import Component, Scan


class CycloneDXGenerator:
    """Generate CycloneDX 1.7 JSON SBOM."""

    SPEC_VERSION = "1.7"
    BOM_FORMAT = "CycloneDX"

    def generate(self, scan: Scan, components: list[Component], edges: list, metadata=None) -> dict:
        """Generate a complete CycloneDX 1.7 BOM."""
        bom_components = []
        for component in components:
            comp_dict = {
                "type": "library",
                "bom-ref": component.id,
                "name": component.name,
                "properties": [
                    {"name": "codesupply:ecosystem", "value": component.ecosystem},
                    {
                        "name": "codesupply:dependency-type",
                        "value": component.dependency_type,
                    },
                    {
                        "name": "codesupply:source-file",
                        "value": component.source_file or "",
                    },
                ],
            }
            if component.version:
                comp_dict["version"] = component.version
            if component.purl:
                comp_dict["purl"] = component.purl
            if component.license:
                comp_dict["licenses"] = [{"license": {"name": component.license}}]
            bom_components.append(comp_dict)

        dependencies = []
        # Group edges by source component
        deps_map = {}
        for edge in edges:
            if edge.source_component_id not in deps_map:
                deps_map[edge.source_component_id] = []
            deps_map[edge.source_component_id].append(edge.target_component_id)

        for ref, depends_on in deps_map.items():
            dependencies.append({"ref": ref, "dependsOn": depends_on})

        return {
            "bomFormat": self.BOM_FORMAT,
            "specVersion": self.SPEC_VERSION,
            "serialNumber": f"urn:uuid:{uuid.uuid4()}",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tools": {
                    "components": [
                        {
                            "name": "CodeSupply",
                            "version": "1.0.0",
                            "type": "application",
                        }
                    ]
                },
                "component": {
                    "type": "application",
                    "name": scan.filename,
                    "bom-ref": scan.id,
                },
            },
            "components": bom_components,
            "dependencies": dependencies,
        }
