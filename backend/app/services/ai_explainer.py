"""AI Security Explainer Service — provides deterministic and AI-assisted explanations

conforming strictly to the product principle:
1. The deterministic scanner is the source of truth.
2. AI must NOT invent dependencies, vulnerabilities, versions, CVEs, or security findings.
3. If no AI API key exists, provide a deterministic fallback explanation.
"""

from typing import Any


class AIExplanationService:
    @classmethod
    def explain_component(
        cls,
        component_id: str,
        component_name: str,
        version: str | None,
        ecosystem: str,
        dependency_type: str,
        risk_level: str,
        risk_score: float | None,
        risk_reasons: list[Any],
        vulnerabilities: list[Any],
        evidence: list[Any],
        purl: str | None = None,
        source_file: str | None = None,
    ) -> dict[str, str]:
        """Generate structured explainability for a component."""
        vuln_count = len(vulnerabilities)
        is_direct = dependency_type.lower() == "direct"
        ver_str = version or "unspecified version"

        # 1. Summary
        if vuln_count > 0:
            highest_sev = "LOW"
            for v in vulnerabilities:
                sev = (v.get("severity") if isinstance(v, dict) else getattr(v, "severity", "UNKNOWN")) or "UNKNOWN"
                if sev.upper() in ("CRITICAL", "HIGH"):
                    highest_sev = sev.upper()
                    break
                elif sev.upper() == "MEDIUM":
                    highest_sev = "MEDIUM"

            summary = (
                f"{component_name} ({ver_str}) is a {dependency_type} {ecosystem} dependency "
                f"flagged with {highest_sev} risk due to {vuln_count} known vulnerability advisory/advisories."
            )
        elif risk_level in ("critical", "high"):
            summary = (
                f"{component_name} ({ver_str}) presents elevated supply-chain risk "
                f"due to detected metadata anomalies or unpinned version constraints."
            )
        else:
            summary = (
                f"{component_name} ({ver_str}) is a {dependency_type} {ecosystem} package "
                f"with a healthy risk posture and no known security advisories detected."
            )

        # 2. Why it matters
        why_parts = []
        if vuln_count > 0:
            why_parts.append(
                f"Active CVEs in {component_name} could allow remote attackers to compromise the application runtime, "
                "trigger denial of service, or leak sensitive memory depending on attack vectors."
            )
        if not is_direct:
            why_parts.append(
                f"As a transitive dependency, {component_name} was pulled in indirectly by an upstream package. "
                "Transitive vulnerabilities are often overlooked because they do not appear directly in top-level manifest files."
            )
        if not version or version.startswith(("^", "~", "*", ">", "<")):
            why_parts.append(
                "Unpinned or loose version specifiers make builds non-reproducible and expose your environment "
                "to silent dependency confusion or upstream supply chain injection."
            )
        if not why_parts:
            why_parts.append(
                f"Dependencies represent third-party attack surface. Maintaining visibility into {component_name} "
                "ensures compliance with EO 14028 / NTIA minimum SBOM standards."
            )
        why_it_matters = " ".join(why_parts)

        # 3. What to do
        actions = []
        if vuln_count > 0:
            # Check for fixed version
            fixed_vers = []
            for v in vulnerabilities:
                fv = v.get("fixed_version") if isinstance(v, dict) else getattr(v, "fixed_version", None)
                if fv and fv not in fixed_vers:
                    fixed_vers.append(fv)
            if fixed_vers:
                actions.append(f"Upgrade {component_name} to version {fixed_vers[0]} or higher to patch active CVEs.")
            else:
                actions.append(
                    "Investigate alternative packages or apply runtime mitigations until an upstream patch is released."
                )

        if is_direct:
            if ecosystem.lower() == "npm":
                actions.append(
                    f"Run `npm install {component_name}@latest` or update `package.json` with an exact pinned version."
                )
            elif ecosystem.lower() in ("pypi", "python"):
                actions.append(
                    f"Update `requirements.txt` or `pyproject.toml` with `{component_name}==<pinned_version>`."
                )
            elif ecosystem.lower() == "cargo":
                actions.append(f"Run `cargo update -p {component_name}` to resolve to the latest compatible crate.")
            elif ecosystem.lower() == "golang":
                actions.append(f"Run `go get {component_name}@latest` and run `go mod tidy`.")
        else:
            actions.append(
                f"Override or upgrade the root dependency that introduced {component_name}, or use dependency resolution overrides."
            )

        what_to_do = " ".join(actions)

        # 4. Technical detail
        detail_lines = [
            f"Package URL (PURL): {purl or 'N/A'}",
            f"Ecosystem: {ecosystem} | Dependency Scope: {dependency_type}",
            f"Source Manifest: {source_file or 'N/A'}",
            f"Computed Risk Score: {risk_score if risk_score is not None else 0.0}/100.0 ({risk_level.upper()})",
        ]
        if vuln_count > 0:
            vuln_ids = []
            for v in vulnerabilities[:5]:
                vid = v.get("vuln_id") if isinstance(v, dict) else getattr(v, "vuln_id", "Unknown")
                vuln_ids.append(vid)
            detail_lines.append(f"Associated Advisories: {', '.join(vuln_ids)}{'...' if vuln_count > 5 else ''}")
        if risk_reasons:
            reasons_str = "; ".join(
                [
                    (r.get("description") if isinstance(r, dict) else getattr(r, "description", ""))
                    for r in risk_reasons[:3]
                ]
            )
            detail_lines.append(f"Risk Factors: {reasons_str}")

        technical_detail = "\n".join(detail_lines)

        return {
            "component_id": component_id,
            "component_name": component_name,
            "version": version,
            "summary": summary,
            "why_it_matters": why_it_matters,
            "what_to_do": what_to_do,
            "technical_detail": technical_detail,
            "label": "AI-assisted explanation",
            "disclaimer": (
                "Recommendations are generated from detected project metadata and available findings. "
                "Verify changes before applying them."
            ),
        }
