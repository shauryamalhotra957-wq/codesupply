import datetime
import uuid
from typing import Any, Dict, List, Optional

from scanner.normalization.normalizer import NormalizedComponent


class CycloneDXGenerator:
    """
    Generates standard-compliant CycloneDX v1.5 JSON SBOMs
    including BOM metadata, components, PURLs, hashes, and dependency DAG.
    """

    @classmethod
    def generate_sbom(
        cls,
        project_name: str,
        components: List[NormalizedComponent],
        cyclonedx_dependencies: Optional[List[Dict[str, Any]]] = None,
        project_version: str = "1.0.0",
    ) -> Dict[str, Any]:
        bom_serial = f"urn:uuid:{uuid.uuid4()}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        root_purl = f"pkg:generic/{project_name}@{project_version}"

        cdx_components: List[Dict[str, Any]] = []

        for comp in components:
            cdx_comp: Dict[str, Any] = {
                "type": "library",
                "name": comp.name,
                "version": comp.version or "unspecified",
                "purl": comp.purl,
                "scope": comp.scope if comp.scope in ("required", "optional", "excluded") else "required",
                "properties": [
                    {"name": "codesupply:ecosystem", "value": comp.ecosystem},
                    {"name": "codesupply:direct", "value": str(comp.direct).lower()},
                    {"name": "codesupply:source_file", "value": comp.source_file},
                ],
            }

            # License info if present
            if comp.license:
                cdx_comp["licenses"] = [
                    {
                        "license": {
                            "id": comp.license if comp.license in ("MIT", "Apache-2.0", "BSD-3-Clause", "GPL-3.0", "ISC") else None,
                            "name": comp.license,
                        }
                    }
                ]

            # Integrity hash if present (e.g., sha512-... in npm lockfiles)
            if comp.integrity:
                if comp.integrity.startswith("sha512-"):
                    cdx_comp["hashes"] = [{"alg": "SHA-512", "content": comp.integrity[7:]}]
                elif comp.integrity.startswith("sha256-"):
                    cdx_comp["hashes"] = [{"alg": "SHA-256", "content": comp.integrity[7:]}]
                elif comp.integrity.startswith("sha1-"):
                    cdx_comp["hashes"] = [{"alg": "SHA-1", "content": comp.integrity[5:]}]

            # External reference if resolved URL present
            if comp.resolved_url:
                cdx_comp["externalReferences"] = [
                    {
                        "type": "distribution",
                        "url": comp.resolved_url,
                    }
                ]

            cdx_components.append(cdx_comp)

        # Build dependencies list if not provided
        if cyclonedx_dependencies is None:
            root_deps = [c.purl for c in components if c.direct]
            cyclonedx_dependencies = [{"ref": root_purl, "dependsOn": root_deps}]
            for c in components:
                if c.dependencies:
                    # Find child purls
                    child_purls = [
                        sub.purl for sub in components if sub.name.lower() in [d.lower() for d in c.dependencies]
                    ]
                    if child_purls:
                        cyclonedx_dependencies.append({"ref": comp.purl, "dependsOn": child_purls})

        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": bom_serial,
            "version": 1,
            "metadata": {
                "timestamp": timestamp,
                "tools": [
                    {
                        "vendor": "CodeSupply",
                        "name": "CodeSupply SBOM Engine",
                        "version": "1.0.0",
                    }
                ],
                "component": {
                    "type": "application",
                    "name": project_name,
                    "version": project_version,
                    "purl": root_purl,
                    "description": f"Generated Software Bill of Materials for {project_name}",
                },
            },
            "components": cdx_components,
            "dependencies": cyclonedx_dependencies,
        }

        return sbom
