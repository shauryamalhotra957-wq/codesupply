"""Unit tests for RemediationEngine."""

from app.models.models import Component, VulnerabilityFinding
from app.remediation.engine import RemediationEngine


def test_generate_commands():
    assert RemediationEngine.generate_command("npm", "lodash", "4.17.21") == "npm install lodash@4.17.21"
    assert RemediationEngine.generate_command("pypi", "urllib3", "2.0.7") == "pip install --upgrade urllib3==2.0.7"
    assert RemediationEngine.generate_command("cargo", "tokio", "1.38.0") == "cargo update -p tokio --precise 1.38.0"
    assert (
        RemediationEngine.generate_command("golang", "golang.org/x/crypto", "0.17.0")
        == "go get golang.org/x/crypto@v0.17.0"
    )
    assert "<version>2.15.0</version>" in RemediationEngine.generate_command(
        "maven", "com.fasterxml.jackson.core:jackson-databind", "2.15.0"
    )


def test_calculate_breaking_risk():
    assert RemediationEngine.calculate_breaking_risk("4.17.15", "4.17.21") == "low"
    assert RemediationEngine.calculate_breaking_risk("1.2.3", "2.0.0") == "high"


def test_generate_remediations():
    c1 = Component(id="c1", scan_id="s1", name="axios", version="0.21.1", ecosystem="npm")
    c2 = Component(id="c2", scan_id="s1", name="flask", version="1.0.2", ecosystem="pypi")

    vulns = [
        VulnerabilityFinding(
            id="v1",
            scan_id="s1",
            component_id="c1",
            vuln_id="CVE-2021-3749",
            severity="high",
            cvss_score=7.5,
            fixed_version="0.21.2",
        ),
        VulnerabilityFinding(
            id="v2",
            scan_id="s1",
            component_id="c2",
            vuln_id="CVE-2019-1010083",
            severity="critical",
            cvss_score=9.8,
            fixed_version="2.0.0",
        ),
    ]

    actions = RemediationEngine.generate_remediations([c1, c2], vulns)
    assert len(actions) == 2

    # Top action should be critical (flask)
    top = actions[0]
    assert top.component_name == "flask"
    assert top.severity == "critical"
    assert top.target_version == "2.0.0"
    assert top.breaking_change_risk == "high"
    assert "pip install --upgrade flask==2.0.0" in top.upgrade_command

    # Second action should be high (axios)
    second = actions[1]
    assert second.component_name == "axios"
    assert second.severity == "high"
    assert second.target_version == "0.21.2"
    assert second.breaking_change_risk == "low"
    assert "npm install axios@0.21.2" in second.upgrade_command
