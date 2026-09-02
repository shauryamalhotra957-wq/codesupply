import datetime
import re
import uuid
from typing import Any, Dict, List, Optional

from scanner.normalization.normalizer import NormalizedComponent


class SPDXGenerator:
    """
    Generates standard-compliant SPDX v2.3 JSON SBOM documents
    including packages, external PURL references, licenses, and dependency relationships.
    """

    @classmethod
    def generate_sbom(
        cls,
        project_name: str,
        components: List[NormalizedComponent],
        project_version: str = "1.0.0",
    ) -> Dict[str, Any]:
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        doc_uuid = uuid.uuid4()
        namespace = f"https://codesupply.dev/spdx/{project_name}-{doc_uuid}"
        root_spdxid = "SPDXRef-Package-Root"

        packages: List[Dict[str, Any]] = [
            {
                "SPDXID": root_spdxid,
                "name": project_name,
                "versionInfo": project_version,
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION",
                "copyrightText": "NOASSERTION",
            }
        ]

        relationships: List[Dict[str, str]] = [
            {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": root_spdxid,
            }
        ]

        for comp in components:
            clean_name = re.sub(r"[^a-zA-Z0-9.\-]", "-", f"{comp.ecosystem}-{comp.name}")
            pkg_spdxid = f"SPDXRef-Package-{clean_name}"

            pkg_entry: Dict[str, Any] = {
                "SPDXID": pkg_spdxid,
                "name": comp.name,
                "versionInfo": comp.version or "unspecified",
                "downloadLocation": comp.resolved_url or "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": comp.license or "NOASSERTION",
                "licenseDeclared": comp.license or "NOASSERTION",
                "copyrightText": "NOASSERTION",
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": comp.purl,
                    }
                ],
            }

            if comp.integrity:
                if comp.integrity.startswith("sha512-"):
                    pkg_entry["checksums"] = [{"algorithm": "SHA512", "checksumValue": comp.integrity[7:]}]
                elif comp.integrity.startswith("sha256:"):
                    pkg_entry["checksums"] = [{"algorithm": "SHA256", "checksumValue": comp.integrity[7:]}]
                elif comp.integrity.startswith("sha256-"):
                    pkg_entry["checksums"] = [{"algorithm": "SHA256", "checksumValue": comp.integrity[7:]}]

            packages.append(pkg_entry)

            if comp.direct:
                relationships.append(
                    {
                        "spdxElementId": root_spdxid,
                        "relationshipType": "DEPENDS_ON",
                        "relatedSpdxElement": pkg_spdxid,
                    }
                )

        return {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": project_name,
            "documentNamespace": namespace,
            "creationInfo": {
                "created": timestamp,
                "creators": ["Tool: CodeSupply-1.0.0", "Organization: CodeSupply"],
            },
            "documentDescribes": [root_spdxid],
            "packages": packages,
            "relationships": relationships,
        }
