from typing import Any, Dict, List, Optional


class SarifGenerator:
    """
    Generates standard OASIS SARIF v2.1.0 (Static Analysis Results Interchange Format)
    reports from CodeSupply scan findings and vulnerabilities for direct integration
    with GitHub Code Scanning and CI/CD security gates.
    """

    SEVERITY_TO_SARIF_LEVEL = {
        "critical": "error",
        "high": "error",
        "medium": "warning",
        "low": "note",
        "info": "note",
    }

    @classmethod
    def generate_sarif(
        cls,
        project_name: str,
        findings: List[Dict[str, Any]],
        components: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Builds a compliant SARIF 2.1.0 JSON representation.
        """
        rules_map: Dict[str, Dict[str, Any]] = {}
        results: List[Dict[str, Any]] = []

        components_by_name = {}
        if components:
            for c in components:
                name = c.get("name", "").lower()
                components_by_name[name] = c

        for idx, finding in enumerate(findings):
            category = finding.get("category", "supply-chain-risk")
            severity = finding.get("severity", "medium").lower()
            sarif_level = cls.SEVERITY_TO_SARIF_LEVEL.get(severity, "warning")
            rule_id = f"CS-{category.upper().replace(' ', '-')}"

            if rule_id not in rules_map:
                rules_map[rule_id] = {
                    "id": rule_id,
                    "name": category.replace("-", " ").title().replace(" ", ""),
                    "shortDescription": {
                        "text": finding.get("title", f"CodeSupply Finding: {category}")
                    },
                    "fullDescription": {
                        "text": finding.get("explanation", "Detected software supply chain risk or vulnerability.")
                    },
                    "defaultConfiguration": {
                        "level": sarif_level
                    },
                    "help": {
                        "text": finding.get("recommendation", "Upgrade the affected dependency to a patched version.")
                    },
                    "properties": {
                        "category": category,
                        "tags": ["security", "supply-chain", "sbom", severity],
                    },
                }

            comp_name = finding.get("component_name", "")
            comp = components_by_name.get(comp_name.lower(), {})
            source_file = comp.get("source_file") or finding.get("source_file") or "manifest"

            msg_text = (
                f"[{severity.upper()}] {finding.get('title', 'Supply chain issue')} in {comp_name}. "
                f"{finding.get('evidence', '')} - Recommendation: {finding.get('recommendation', 'Update package')}"
            )

            result_entry = {
                "ruleId": rule_id,
                "ruleIndex": list(rules_map.keys()).index(rule_id),
                "level": sarif_level,
                "message": {
                    "text": msg_text
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": source_file.replace("\\", "/")
                            },
                            "region": {
                                "startLine": 1,
                                "startColumn": 1
                            }
                        }
                    }
                ],
                "properties": {
                    "component": comp_name,
                    "severity": severity,
                    "purl": comp.get("purl", "")
                }
            }
            results.append(result_entry)

        return {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "CodeSupply",
                            "version": "1.2.0",
                            "informationUri": "https://github.com/shauryamalhotra957-wq/codesupply",
                            "semanticVersion": "1.2.0",
                            "rules": list(rules_map.values()),
                        }
                    },
                    "invocations": [
                        {
                            "executionSuccessful": True,
                        }
                    ],
                    "artifacts": [
                        {"location": {"uri": p}}
                        for p in set(
                            r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
                            for r in results
                            if r.get("locations")
                        )
                    ],
                    "results": results,
                }
            ],
        }
