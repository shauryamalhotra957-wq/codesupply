"""
SBOM Comparison & Dependency Drift Differ
Calculates deterministic structural, version, and vulnerability diffs
between two SBOM inventories or project snapshots.
"""

from typing import Any, Dict, List, Optional
from scanner.security.vuln_engine import VulnerabilityEngine


class SbomDiffer:
    @staticmethod
    def compare_projects(
        base_project_id: str,
        target_project_id: str,
        base_components: List[Dict[str, Any]],
        target_components: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Compute the full delta between a base project and target project."""
        base_map: Dict[str, Dict[str, Any]] = {
            f"{c.get('ecosystem')}:{c.get('name')}".lower(): c for c in base_components
        }
        target_map: Dict[str, Dict[str, Any]] = {
            f"{c.get('ecosystem')}:{c.get('name')}".lower(): c for c in target_components
        }

        added_components: List[Dict[str, Any]] = []
        removed_components: List[Dict[str, Any]] = []
        version_changes: List[Dict[str, Any]] = []

        # Find added and version-changed components
        for key, target_comp in target_map.items():
            if key not in base_map:
                added_components.append(target_comp)
            else:
                base_comp = base_map[key]
                base_ver = base_comp.get("version") or ""
                target_ver = target_comp.get("version") or ""
                if base_ver != target_ver:
                    base_tuple = VulnerabilityEngine.parse_version_tuple(base_ver)
                    target_tuple = VulnerabilityEngine.parse_version_tuple(target_ver)
                    change_type = "UPGRADE" if target_tuple >= base_tuple else "DOWNGRADE"
                    version_changes.append({
                        "name": target_comp.get("name"),
                        "ecosystem": target_comp.get("ecosystem"),
                        "old_version": base_ver,
                        "new_version": target_ver,
                        "change_type": change_type,
                    })

        # Find removed components
        for key, base_comp in base_map.items():
            if key not in target_map:
                removed_components.append(base_comp)

        # Calculate Vulnerability Deltas
        base_vulns = []
        for c in base_components:
            for v in VulnerabilityEngine.match_component(
                c.get("name", ""), c.get("version"), c.get("ecosystem", "")
            ):
                base_vulns.append(v)

        target_vulns = []
        for c in target_components:
            for v in VulnerabilityEngine.match_component(
                c.get("name", ""), c.get("version"), c.get("ecosystem", "")
            ):
                target_vulns.append(v)

        base_cve_ids = {v["cve_id"] for v in base_vulns}
        target_cve_ids = {v["cve_id"] for v in target_vulns}

        new_vulnerabilities = [v for v in target_vulns if v["cve_id"] not in base_cve_ids]
        resolved_vulnerabilities = [v for v in base_vulns if v["cve_id"] not in target_cve_ids]

        return {
            "base_project_id": base_project_id,
            "target_project_id": target_project_id,
            "total_base_components": len(base_components),
            "total_target_components": len(target_components),
            "added_count": len(added_components),
            "removed_count": len(removed_components),
            "version_changes_count": len(version_changes),
            "added_components": added_components,
            "removed_components": removed_components,
            "version_changes": version_changes,
            "new_vulnerabilities": new_vulnerabilities,
            "resolved_vulnerabilities": resolved_vulnerabilities,
            "net_vulnerability_delta": len(new_vulnerabilities) - len(resolved_vulnerabilities),
        }
