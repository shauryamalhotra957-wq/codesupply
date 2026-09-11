"""Automated Remediation Engine — Prescriptive upgrade commands and vulnerability elimination."""

import re
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class RemediationAction:
    component_id: str
    component_name: str
    current_version: str
    ecosystem: str
    target_version: str
    upgrade_command: str
    severity: str
    max_cvss_score: float | None
    vulns_fixed: list[str]
    breaking_change_risk: str
    risk_reduction_score: float
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RemediationEngine:
    """Calculates prioritized dependency upgrade recommendations with executable CLI commands."""

    SEVERITY_WEIGHTS = {
        "critical": 10.0,
        "high": 7.5,
        "medium": 4.0,
        "low": 1.5,
        "info": 0.5,
        "none": 0.0,
    }

    @classmethod
    def generate_command(cls, ecosystem: str, name: str, target_version: str) -> str:
        """Generate ecosystem-accurate CLI upgrade command."""
        eco = (ecosystem or "").lower()
        if eco in ("npm", "javascript", "node"):
            return f"npm install {name}@{target_version}"
        elif eco in ("pypi", "python", "pip"):
            return f"pip install --upgrade {name}=={target_version}"
        elif eco in ("maven", "java"):
            return f"# Update <version>{target_version}</version> for {name} in pom.xml"
        elif eco in ("cargo", "rust", "crates.io"):
            return f"cargo update -p {name} --precise {target_version}"
        elif eco in ("golang", "go"):
            prefix = "" if target_version.startswith("v") else "v"
            return f"go get {name}@{prefix}{target_version}"
        return f"# Upgrade {name} to {target_version}"

    @classmethod
    def calculate_breaking_risk(cls, current: str, target: str) -> str:
        """Estimate breaking change risk using semantic version major comparison."""
        cur_match = re.match(r"^v?(\d+)", current.strip())
        tgt_match = re.match(r"^v?(\d+)", target.strip())

        if cur_match and tgt_match:
            cur_major = int(cur_match.group(1))
            tgt_major = int(tgt_match.group(1))
            if tgt_major > cur_major:
                return "high"
            return "low"
        return "medium"

    @classmethod
    def generate_remediations(
        cls,
        components: list[Any],
        vulnerabilities: list[Any],
    ) -> list[RemediationAction]:
        """Generate prioritized remediation actions grouped by component."""
        comp_map = {c.id: c for c in components}

        # Group vulnerabilities by component_id
        vulns_by_comp: dict[str, list[Any]] = {}
        for v in vulnerabilities:
            vulns_by_comp.setdefault(v.component_id, []).append(v)

        actions: list[RemediationAction] = []

        for comp_id, vulns in vulns_by_comp.items():
            comp = comp_map.get(comp_id)
            if not comp:
                continue

            # Find target fixed version (take the latest fixed version available)
            fixed_versions = [v.fixed_version for v in vulns if v.fixed_version]
            if not fixed_versions:
                # No fixed version yet
                continue

            # Pick target version (highest/first fixed version)
            target_ver = fixed_versions[0]
            for fv in fixed_versions:
                if fv > target_ver:
                    target_ver = fv

            # Calculate highest severity and max CVSS
            highest_sev = "low"
            highest_sev_val = 0
            max_cvss = None
            vuln_ids = []

            for v in vulns:
                vuln_ids.append(v.vuln_id)
                sev = (v.severity or "medium").lower()
                weight = cls.SEVERITY_WEIGHTS.get(sev, 1.0)
                if weight > highest_sev_val:
                    highest_sev_val = weight
                    highest_sev = sev

                if v.cvss_score is not None:
                    if max_cvss is None or float(v.cvss_score) > max_cvss:
                        max_cvss = float(v.cvss_score)

            breaking_risk = cls.calculate_breaking_risk(comp.version or "0.0.0", target_ver)
            command = cls.generate_command(comp.ecosystem or "generic", comp.name, target_ver)

            # Risk reduction score
            base_risk = max_cvss if max_cvss is not None else highest_sev_val
            risk_reduction = round(base_risk * (1.2 if len(vulns) > 1 else 1.0), 1)

            rationale = (
                f"Upgrading from {comp.version} to {target_ver} patches {len(vuln_ids)} "
                f"vulnerabilities ({', '.join(vuln_ids[:3])}{'...' if len(vuln_ids) > 3 else ''}) "
                f"with {breaking_risk} breaking risk."
            )

            actions.append(
                RemediationAction(
                    component_id=comp.id,
                    component_name=comp.name,
                    current_version=comp.version or "unknown",
                    ecosystem=comp.ecosystem or "generic",
                    target_version=target_ver,
                    upgrade_command=command,
                    severity=highest_sev,
                    max_cvss_score=max_cvss,
                    vulns_fixed=vuln_ids,
                    breaking_change_risk=breaking_risk,
                    risk_reduction_score=risk_reduction,
                    rationale=rationale,
                )
            )

        # Sort by highest severity weight descending, then max_cvss descending
        actions.sort(
            key=lambda a: (
                cls.SEVERITY_WEIGHTS.get(a.severity.lower(), 0),
                a.max_cvss_score or 0.0,
                a.risk_reduction_score,
            ),
            reverse=True,
        )

        return actions
