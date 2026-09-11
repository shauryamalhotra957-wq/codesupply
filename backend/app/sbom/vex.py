"""VEX (Vulnerability Exploitability eXchange) Generator for CycloneDX 1.7 and OpenVEX."""

import uuid
from datetime import datetime, timezone
from typing import Any


class VEXGenerator:
    """Generates machine-readable VEX statements complying with CISA and CycloneDX 1.7 standards."""

    @staticmethod
    def generate_cyclonedx_vex(scan: Any, components: list[Any], vulnerabilities: list[Any]) -> dict[str, Any]:
        """Generate a CycloneDX 1.7 VEX document."""
        now_iso = datetime.now(timezone.utc).isoformat()
        comp_map = {c.id: c for c in components}

        vuln_entries = []
        for v in vulnerabilities:
            comp = comp_map.get(v.component_id)
            purl = comp.purl if comp else None
            comp_name = comp.name if comp else (getattr(v, "component_name", None) or "unknown")

            severity_str = (v.severity or "medium").lower()
            if severity_str not in ("critical", "high", "medium", "low", "info", "none"):
                severity_str = "medium"

            ratings = []
            if v.cvss_score is not None:
                ratings.append(
                    {
                        "source": {"name": "NIST-NVD"},
                        "score": float(v.cvss_score),
                        "severity": severity_str,
                        "method": "CVSSv31",
                        "vector": v.cvss_vector or "",
                    }
                )
            else:
                ratings.append(
                    {
                        "source": {"name": "OSV"},
                        "severity": severity_str,
                    }
                )

            # Determine VEX state
            if v.fixed_version:
                state = "exploitable"
                response = ["update"]
                detail = f"Component {comp_name} is affected. A fixed release ({v.fixed_version}) is available."
            else:
                state = "in_triage"
                response = ["workaround_available"]
                detail = f"Component {comp_name} is affected. No official upstream fix is currently published."

            affects = []
            if purl:
                affects.append({"ref": purl})
            elif comp:
                affects.append({"ref": f"urn:codesupply:component:{comp.id}"})

            vuln_entry: dict[str, Any] = {
                "bom-ref": f"vex-{v.vuln_id}-{v.id[:8]}",
                "id": v.vuln_id,
                "source": {
                    "name": "OSV.dev",
                    "url": f"https://osv.dev/vulnerability/{v.vuln_id}",
                },
                "ratings": ratings,
                "description": v.summary or "No summary provided",
                "analysis": {
                    "state": state,
                    "detail": detail,
                    "response": response,
                },
                "affects": affects,
            }

            if v.references and isinstance(v.references, list):
                vuln_entry["advisories"] = [{"url": ref} for ref in v.references[:5]]

            vuln_entries.append(vuln_entry)

        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.7",
            "serialNumber": f"urn:uuid:{uuid.uuid4()}",
            "version": 1,
            "metadata": {
                "timestamp": now_iso,
                "tools": {
                    "components": [
                        {
                            "type": "application",
                            "name": "CodeSupply",
                            "version": "1.2.0",
                            "vendor": "Smart India Hackathon (SIH1449)",
                        }
                    ]
                },
                "component": {
                    "type": "application",
                    "name": scan.project_name or scan.filename or "project",
                    "version": "1.0.0",
                },
            },
            "vulnerabilities": vuln_entries,
        }

    @staticmethod
    def generate_openvex(scan: Any, components: list[Any], vulnerabilities: list[Any]) -> dict[str, Any]:
        """Generate an OpenVEX (openvex.dev) specification compliant document."""
        now_iso = datetime.now(timezone.utc).isoformat()
        comp_map = {c.id: c for c in components}

        statements = []
        for v in vulnerabilities:
            comp = comp_map.get(v.component_id)
            c_name = comp.name if comp else (getattr(v, "component_name", None) or "unknown")
            c_ver = comp.version if comp else (getattr(v, "component_version", None) or "0.0.0")
            purl = comp.purl if comp else f"pkg:generic/{c_name}@{c_ver}"
            status = "affected" if not v.fixed_version else "fixed"

            statement = {
                "vulnerability": {
                    "name": v.vuln_id,
                    "description": v.summary or "",
                },
                "products": [purl],
                "status": status,
                "timestamp": now_iso,
                "action_statement": f"Upgrade to version {v.fixed_version}"
                if v.fixed_version
                else "Monitor upstream advisory for patched release",
            }
            statements.append(statement)

        return {
            "@context": "https://openvex.dev/ns/v0.2.0",
            "@id": f"https://codesupply.dev/vex/{scan.id}",
            "author": "CodeSupply VEX Engine (SIH1449)",
            "role": "Security Assessment Tool",
            "timestamp": now_iso,
            "version": 1,
            "statements": statements,
        }
