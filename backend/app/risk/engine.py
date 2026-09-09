"""Deterministic rule-based risk scoring engine."""

from dataclasses import dataclass, field


@dataclass
class RiskReasonData:
    """A single reason contributing to a component's risk assessment."""

    reason_type: str
    description: str
    severity_contribution: float


@dataclass
class RiskAssessment:
    """Complete risk assessment for a component."""

    risk_level: str  # critical, high, medium, low, none, unknown
    risk_score: float  # 0-100
    reasons: list[RiskReasonData] = field(default_factory=list)


class RiskEngine:
    """Deterministic, rule-based risk scoring.

    Algorithm:
    1. Start with score = 0
    2. For each applicable rule, add its weight to the score
    3. Cap at 100
    4. Map score to risk level using thresholds

    Thresholds:
        critical: >= 80
        high:     >= 60
        medium:   >= 30
        low:      >= 10
        none:     < 10 (with some signal)
        unknown:  when intelligence unavailable and no other signals

    Rule weights are documented below and are the same for every run
    (deterministic: same inputs → same outputs).
    """

    RULES = {
        "critical_vulnerability": 40,
        "high_vulnerability": 30,
        "medium_vulnerability": 15,
        "low_vulnerability": 5,
        "missing_version": 10,
        "version_ambiguity": 8,
        "intelligence_unavailable": 12,
        "low_analysis_confidence": 5,
    }

    def assess_component(self, component, vulnerabilities: list, lookup_status: str) -> RiskAssessment:
        """Calculate risk for a single component.

        Args:
            component: Component ORM object
            vulnerabilities: List of VulnerabilityFinding ORM objects
            lookup_status: Status string (checked, unavailable, cached, not_applicable, unknown)
        """
        score = 0.0
        reasons: list[RiskReasonData] = []

        # Vulnerability-based risk
        for vuln in vulnerabilities:
            sev = (vuln.severity or "unknown").lower()

            if sev == "critical":
                weight = self.RULES["critical_vulnerability"]
                reasons.append(
                    RiskReasonData(
                        "critical_vulnerability",
                        f"Critical vulnerability {vuln.vuln_id}: {vuln.summary or 'No details'}",
                        weight,
                    )
                )
            elif sev == "high":
                weight = self.RULES["high_vulnerability"]
                reasons.append(
                    RiskReasonData(
                        "high_vulnerability",
                        f"High severity vulnerability {vuln.vuln_id}: {vuln.summary or 'No details'}",
                        weight,
                    )
                )
            elif sev == "medium":
                weight = self.RULES["medium_vulnerability"]
                reasons.append(
                    RiskReasonData(
                        "medium_vulnerability",
                        f"Medium severity vulnerability {vuln.vuln_id}: {vuln.summary or 'No details'}",
                        weight,
                    )
                )
            else:
                weight = self.RULES["low_vulnerability"]
                reasons.append(
                    RiskReasonData(
                        "low_vulnerability",
                        f"Vulnerability {vuln.vuln_id}: {vuln.summary or 'No details'}",
                        weight,
                    )
                )

            score += weight

            # Add fixed-version reason if available
            if vuln.fixed_version:
                reasons.append(
                    RiskReasonData(
                        "fix_available",
                        f"Fixed version available: {vuln.fixed_version}",
                        0,  # Informational, doesn't add to score
                    )
                )

        # Version-based risk
        if not component.version:
            weight = self.RULES["missing_version"]
            score += weight
            reasons.append(
                RiskReasonData(
                    "missing_version",
                    "Component version is unknown — cannot determine vulnerability status",
                    weight,
                )
            )
        elif component.version_confidence in ("declared_range", "inferred"):
            weight = self.RULES["version_ambiguity"]
            score += weight
            reasons.append(
                RiskReasonData(
                    "version_ambiguity",
                    f"Version is a declared range ({component.original_declaration or component.version}), not an exact resolution",
                    weight,
                )
            )

        # Intelligence availability
        if lookup_status == "unavailable":
            weight = self.RULES["intelligence_unavailable"]
            score += weight
            reasons.append(
                RiskReasonData(
                    "intelligence_unavailable",
                    "Vulnerability intelligence was unavailable — this component could not be checked",
                    weight,
                )
            )
        elif lookup_status == "unknown":
            weight = self.RULES["low_analysis_confidence"]
            score += weight
            reasons.append(
                RiskReasonData(
                    "low_analysis_confidence",
                    "Analysis confidence is low for this component",
                    weight,
                )
            )

        # If no risk signals at all
        if not reasons:
            reasons.append(
                RiskReasonData(
                    "no_risk_indicators",
                    "No detected risk indicators",
                    0,
                )
            )

        # Cap score
        score = min(score, 100.0)

        # Determine risk level
        if (
            lookup_status == "unavailable"
            and len(vulnerabilities) == 0
            and score <= self.RULES["intelligence_unavailable"] + self.RULES["missing_version"]
        ):
            risk_level = "unknown"
        elif score >= 80:
            risk_level = "critical"
        elif score >= 60:
            risk_level = "high"
        elif score >= 30:
            risk_level = "medium"
        elif score >= 10:
            risk_level = "low"
        elif score > 0:
            risk_level = "none"
        else:
            risk_level = "none"

        return RiskAssessment(
            risk_level=risk_level,
            risk_score=round(score, 1),
            reasons=reasons,
        )

    def assess_scan(self, components_with_assessments: list[tuple]) -> dict:
        """Aggregate risk assessment for an entire scan.

        Args:
            components_with_assessments: List of (component, RiskAssessment) tuples
        """
        if not components_with_assessments:
            return {
                "overall_risk_score": 0,
                "overall_risk_level": "none",
                "risk_distribution": {},
            }

        max_score = 0.0
        distribution: dict[str, int] = {}

        for _comp, assessment in components_with_assessments:
            max_score = max(max_score, assessment.risk_score)
            distribution[assessment.risk_level] = distribution.get(assessment.risk_level, 0) + 1

        if max_score >= 80:
            overall = "critical"
        elif max_score >= 60:
            overall = "high"
        elif max_score >= 30:
            overall = "medium"
        elif max_score >= 10:
            overall = "low"
        else:
            overall = "none"

        return {
            "overall_risk_score": round(max_score, 1),
            "overall_risk_level": overall,
            "risk_distribution": distribution,
        }
