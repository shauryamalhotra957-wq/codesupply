from typing import List

from backend.services.risk_engine import Finding


class BaseExplanationProvider:
    """Abstract interface for risk explanation providers (rule-based or future LLM)."""

    def explain(self, finding: Finding) -> Finding:
        raise NotImplementedError


class DeterministicExplanationProvider(BaseExplanationProvider):
    """
    Deterministic rule-based provider that generates clear, contextual explanations
    and actionable remediation advice for detected anomalies.
    """

    def explain(self, finding: Finding) -> Finding:
        cat = finding.category
        name = finding.component_name

        if cat == "Version Pinning":
            if "Wildcard" in finding.title:
                finding.explanation = (
                    f"Using a wildcard or loose specifier for '{name}' allows builds to automatically "
                    "pull new upstream versions without testing. A newly released malicious or broken "
                    "version can break production or execute arbitrary code during installation."
                )
                finding.recommendation = (
                    f"Pin '{name}' to a specific tested version (e.g. '{name}==x.y.z' in requirements.txt "
                    f"or '{name}': '~x.y.z' in package.json) and commit a lockfile."
                )
            else:
                finding.explanation = (
                    f"The direct dependency '{name}' does not specify an exact pinned version. "
                    "Unpinned dependencies create non-reproducible builds and expose CI/CD pipelines "
                    "to dependency confusion and automated supply-chain injection attacks."
                )
                finding.recommendation = (
                    f"Determine the current working version of '{name}' and pin it explicitly in your manifest "
                    "(e.g., '{name}==2.32.0'). Utilize lockfiles (`requirements.txt` / `package-lock.json`)."
                )

        elif cat == "Duplicate":
            finding.explanation = (
                f"The package '{name}' is declared multiple times across project manifests. "
                "Duplicate declarations increase build ambiguity, bloat SBOM inventory, and can lead to "
                "unintended version resolution behavior across different build tools."
            )
            finding.recommendation = (
                f"Consolidate declarations of '{name}' into a single authoritative manifest file. "
                "Remove redundant definitions."
            )

        elif cat == "Conflict":
            finding.explanation = (
                f"Different files in your project specify incompatible or conflicting version bounds for '{name}'. "
                "This leads to nondeterministic resolution, runtime incompatibility, or silent build-time overrides."
            )
            finding.recommendation = (
                f"Align version constraints for '{name}' across all manifest files. "
                "Test the application with a unified pinned version."
            )

        elif cat == "Supply Chain":
            finding.explanation = (
                f"Dependency '{name}' is referenced directly via a Git URL or remote archive rather than "
                "an immutable package registry. Remote repositories can be force-pushed, deleted, or hijacked."
            )
            finding.recommendation = (
                f"Publish '{name}' to an internal registry (e.g. PyPI/Verdaccio) or pin the Git reference "
                "to an immutable full 40-character commit SHA."
            )

        elif cat == "Hygiene":
            finding.explanation = (
                f"The component '{name}' is widely recognized as deprecated, unmaintained, or superseded. "
                "Unmaintained libraries do not receive security patches."
            )
            finding.recommendation = f"Migrate from '{name}' to its actively maintained modern alternative as recommended in the evidence note."

        else:
            finding.explanation = (
                f"A supply-chain hygiene anomaly was flagged for component '{name}'. Review the manifest definition."
            )
            finding.recommendation = (
                f"Review '{name}' configuration in your dependency manifests and verify its source integrity."
            )

        return finding


class RiskExplanationService:
    """
    Service responsible for explaining findings and suggesting remediation.
    Core product uses DeterministicExplanationProvider; architecture is ready
    to swap or chain an AI/LLM provider when configured.
    """

    def __init__(self, provider: BaseExplanationProvider = None):
        self.provider = provider or DeterministicExplanationProvider()

    def enrich_findings(self, findings: List[Finding]) -> List[Finding]:
        enriched: List[Finding] = []
        for finding in findings:
            enriched.append(self.provider.explain(finding))
        return enriched
