"""Unit tests for the deterministic risk calculation engine."""

import pytest

from app.models.models import Component, VulnerabilityFinding
from app.risk.engine import RiskEngine


@pytest.fixture
def engine():
    return RiskEngine()


def test_clean_component_risk(engine):
    comp = Component(
        name="clean-pkg",
        version="1.0.0",
        version_confidence="exact",
        ecosystem="npm",
        dependency_type="direct",
        source_file="package-lock.json",
    )

    assessment = engine.assess_component(comp, [], lookup_status="checked")
    assert assessment.risk_level == "none"
    assert assessment.risk_score == 0.0
    assert any("No detected risk indicators" in r.description for r in assessment.reasons)


def test_vulnerability_risk_scoring(engine):
    comp = Component(
        name="lodash",
        version="4.17.20",
        version_confidence="exact",
        ecosystem="npm",
        dependency_type="direct",
        source_file="package-lock.json",
    )
    vuln = VulnerabilityFinding(
        vuln_id="GHSA-jf85-cpcp-j695",
        summary="Prototype Pollution in lodash",
        severity="high",
        fixed_version="4.17.21",
    )

    assessment = engine.assess_component(comp, [vuln], lookup_status="checked")
    assert assessment.risk_score >= 30.0
    assert any(r.reason_type == "high_vulnerability" for r in assessment.reasons)
    assert any(r.reason_type == "fix_available" for r in assessment.reasons)


def test_missing_version_risk(engine):
    comp = Component(
        name="urllib3",
        version=None,
        version_confidence="unknown",
        ecosystem="pypi",
        dependency_type="direct",
        source_file="requirements.txt",
    )

    assessment = engine.assess_component(comp, [], lookup_status="not_applicable")
    assert assessment.risk_score >= 10.0
    assert any(r.reason_type == "missing_version" for r in assessment.reasons)


def test_unavailable_intelligence_honesty(engine):
    """Never mark packages safe when intelligence is unavailable."""
    comp = Component(
        name="some-pkg",
        version="2.0.0",
        version_confidence="exact",
        ecosystem="npm",
        dependency_type="direct",
        source_file="package-lock.json",
    )

    assessment = engine.assess_component(comp, [], lookup_status="unavailable")
    assert assessment.risk_level == "unknown"
    assert any(r.reason_type == "intelligence_unavailable" for r in assessment.reasons)
