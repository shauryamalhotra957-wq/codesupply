import datetime
import re
import uuid
from typing import Any, Dict, List

from app.models.models import Component, DependencyEdge, Scan


class SPDX23Generator:
    """Generates standard-compliant SPDX v2.3 JSON SBOM documents (ISO/IEC 5962:2021)."""

    SPEC_VERSION = "SPDX-2.3"
    DATA_LICENSE = "CC0-1.0"

    def generate(
        self,
        scan: Scan,
        components: List[Component],
        edges: List[DependencyEdge] | None = None,
    ) -> Dict[str, Any]:
        """Generate a compliant SPDX 2.3 JSON document."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        doc_uuid = uuid.uuid4().hex[:12]
        proj_name = scan.project_name or scan.filename or "CodeSupply-Scanned-Project"
        namespace = f"https://codesupply.dev/spdx/{scan.id}-{doc_uuid}"
        root_spdxid = "SPDXRef-Package-Root"

        # Root Project Package
        packages: List[Dict[str, Any]] = [
            {
                "SPDXID": root_spdxid,
                "name": proj_name,
                "versionInfo": "1.0.0",
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION",
                "copyrightText": "NOASSERTION",
                "description": f"Root application package analyzed by CodeSupply (Scan ID: {scan.id})",
            }
        ]

        relationships: List[Dict[str, str]] = [
            {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": root_spdxid,
            }
        ]

        comp_id_to_spdxid: Dict[str, str] = {}

        for comp in components:
            clean_name = re.sub(r"[^a-zA-Z0-9.\-]", "-", f"{comp.ecosystem}-{comp.name}")
            pkg_spdxid = f"SPDXRef-Package-{clean_name}-{comp.id[:8]}"
            comp_id_to_spdxid[comp.id] = pkg_spdxid

            external_refs = []
            if comp.purl:
                external_refs.append(
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": comp.purl,
                    }
                )

            pkg_entry: Dict[str, Any] = {
                "SPDXID": pkg_spdxid,
                "name": comp.name,
                "versionInfo": comp.version or "unspecified",
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": comp.license or "NOASSERTION",
                "licenseDeclared": comp.license or "NOASSERTION",
                "copyrightText": "NOASSERTION",
            }

            if external_refs:
                pkg_entry["externalRefs"] = external_refs

            packages.append(pkg_entry)

            # Direct dependencies are declared as DEPENDS_ON root package
            if comp.dependency_type == "direct":
                relationships.append(
                    {
                        "spdxElementId": root_spdxid,
                        "relationshipType": "DEPENDS_ON",
                        "relatedSpdxElement": pkg_spdxid,
                    }
                )

        # Map edges to SPDX relationships
        if edges:
            for edge in edges:
                src_spdx = comp_id_to_spdxid.get(edge.source_component_id)
                tgt_spdx = comp_id_to_spdxid.get(edge.target_component_id)
                if src_spdx and tgt_spdx:
                    relationships.append(
                        {
                            "spdxElementId": src_spdx,
                            "relationshipType": "DEPENDS_ON",
                            "relatedSpdxElement": tgt_spdx,
                        }
                    )

        return {
            "spdxVersion": self.SPEC_VERSION,
            "dataLicense": self.DATA_LICENSE,
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": proj_name,
            "documentNamespace": namespace,
            "creationInfo": {
                "created": timestamp,
                "creators": [
                    "Tool: CodeSupply-1.2.0",
                    "Organization: CodeSupply Security Team",
                ],
            },
            "packages": packages,
            "relationships": relationships,
        }
