from dataclasses import dataclass
from typing import Any, Dict, List

from scanner.normalization.normalizer import NormalizedComponent
from scanner.parsers.base import ParsedDependency
from scanner.security.vuln_engine import VulnerabilityEngine


@dataclass
class Finding:
    """Represents a deterministic security, hygiene, or supply-chain risk finding."""

    component_name: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str  # Version Pinning, Conflict, Duplicate, Supply Chain, Hygiene
    title: str
    evidence: str
    explanation: str = ""
    recommendation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_name": self.component_name,
            "severity": self.severity,
            "category": self.category,
            "title": self.title,
            "evidence": self.evidence,
            "explanation": self.explanation,
            "recommendation": self.recommendation,
        }


class RiskEngine:
    """
    Deterministic Risk and Supply-Chain Anomaly Engine for CodeSupply.
    Identifies unpinned versions, duplicates, conflicting requirements,
    and supply chain hygiene anomalies.
    """

    KNOWN_DEPRECATED_PACKAGES = {
        "pypi": {
            "pycrypto": "Deprecated and unmaintained. Replace with 'cryptography' or 'pycryptodome'.",
            "python-jwt": "Vulnerable to signature bypass. Upgrade to 'PyJWT>=2.0.0'.",
            "fabric": "Legacy version 1 is unmaintained. Use Fabric 2+ or Invoke.",
        },
        "npm": {
            "request": "Deprecated since 2020. Replace with 'axios', 'got', or native 'fetch'.",
            "left-pad": "Historical risk artifact. Use String.prototype.padStart().",
            "nomnom": "Deprecated CLI parser. Replace with 'commander' or 'yargs'.",
            "querystring": "Node.js core module legacy. Use URLSearchParams.",
        },
    }

    @classmethod
    def analyze(
        cls,
        raw_dependencies: List[ParsedDependency],
        normalized_components: List[NormalizedComponent],
    ) -> List[Finding]:
        findings: List[Finding] = []

        # 1. Check Missing / Unpinned Versions
        for comp in normalized_components:
            if comp.direct and (not comp.version or comp.version in ("unspecified", "unpinned", "")):
                findings.append(
                    Finding(
                        component_name=comp.name,
                        severity="HIGH",
                        category="Version Pinning",
                        title=f"Unpinned Dependency Version: '{comp.name}'",
                        evidence=f"Manifest '{comp.source_file}' specifies '{comp.raw_specifier or 'unpinned'}' without exact version.",
                    )
                )
            elif comp.raw_specifier and comp.raw_specifier.strip() in ("*", "latest"):
                findings.append(
                    Finding(
                        component_name=comp.name,
                        severity="MEDIUM",
                        category="Version Pinning",
                        title=f"Wildcard Version Specifier: '{comp.name}'",
                        evidence=f"Manifest '{comp.source_file}' uses wildcard '{comp.raw_specifier}'.",
                    )
                )

        # 2. Check Duplicate Declarations in Raw Dependencies
        raw_by_key: Dict[str, List[ParsedDependency]] = {}
        for dep in raw_dependencies:
            key = f"{dep.ecosystem}:{dep.name.lower()}"
            raw_by_key.setdefault(key, []).append(dep)

        for key, occurrences in raw_by_key.items():
            if len(occurrences) > 1:
                files = [f"'{o.source_file}' ({o.specifier or 'unpinned'})" for o in occurrences]
                findings.append(
                    Finding(
                        component_name=occurrences[0].name,
                        severity="MEDIUM",
                        category="Duplicate",
                        title=f"Duplicate Dependency Declarations: '{occurrences[0].name}'",
                        evidence=f"Package declared {len(occurrences)} times across: {', '.join(files)}.",
                    )
                )

        # 3. Check Conflicting Version Specifiers
        for key, occurrences in raw_by_key.items():
            specifiers = {o.specifier for o in occurrences if o.specifier}
            if len(specifiers) > 1:
                findings.append(
                    Finding(
                        component_name=occurrences[0].name,
                        severity="HIGH",
                        category="Conflict",
                        title=f"Conflicting Version Requirements: '{occurrences[0].name}'",
                        evidence=f"Conflicting specifiers detected across manifests: {', '.join(specifiers)}.",
                    )
                )

        # 4. Check URL / Git Installations
        for dep in raw_dependencies:
            if dep.metadata.get("url_install"):
                findings.append(
                    Finding(
                        component_name=dep.name,
                        severity="MEDIUM",
                        category="Supply Chain",
                        title=f"Git/URL Dependency Source: '{dep.name}'",
                        evidence=f"Direct URL source in '{dep.source_file}': {dep.metadata['url_install']}.",
                    )
                )

        # 5. Check Deprecated / Known Risky Packages
        for comp in normalized_components:
            eco = comp.ecosystem.lower()
            deprecated_map = cls.KNOWN_DEPRECATED_PACKAGES.get(eco, {})
            if comp.name.lower() in deprecated_map:
                reason = deprecated_map[comp.name.lower()]
                findings.append(
                    Finding(
                        component_name=comp.name,
                        severity="HIGH",
                        category="Hygiene",
                        title=f"Deprecated/EOL Component: '{comp.name}'",
                        evidence=f"Detected package '{comp.name}' in {comp.source_file}. Note: {reason}",
                    )
                )

        # 6. Check Known CVEs and Exploits
        for comp in normalized_components:
            matches = VulnerabilityEngine.match_component(comp.name, comp.version, comp.ecosystem)
            for vuln in matches:
                kev_flag = " [CISA KEV EXPLOITED]" if vuln.get("cisa_kev") else ""
                remed = (
                    f" Recommended fix: upgrade to {vuln.get('remediation_version')}."
                    if vuln.get("remediation_version")
                    else ""
                )
                findings.append(
                    Finding(
                        component_name=comp.name,
                        severity=vuln.get("severity", "HIGH"),
                        category="Vulnerability",
                        title=f"{vuln.get('cve_id')}: {vuln.get('package_name')}{kev_flag}",
                        evidence=f"CVSS v3.1: {vuln.get('cvss_v3_score')} | EPSS: {vuln.get('epss_score') * 100:.1f}% | {vuln.get('summary')}{remed}",
                        explanation=vuln.get("summary", ""),
                        recommendation=vuln.get("remediation_version", ""),
                    )
                )

        return findings
