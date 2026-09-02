import pytest
from scanner.security.vuln_engine import VulnerabilityEngine


def test_version_tuple_parsing():
    assert VulnerabilityEngine.parse_version_tuple("2.31.0") == [2, 31, 0]
    assert VulnerabilityEngine.parse_version_tuple("v1.26.17-alpha") == [1, 26, 17]
    assert VulnerabilityEngine.parse_version_tuple("4") == [4, 0, 0]
    assert VulnerabilityEngine.parse_version_tuple("") == [0, 0, 0]


def test_is_version_vulnerable_ranges():
    # Simple < bound
    assert VulnerabilityEngine.is_version_vulnerable("2.30.0", "<2.31.0") is True
    assert VulnerabilityEngine.is_version_vulnerable("2.31.0", "<2.31.0") is False
    assert VulnerabilityEngine.is_version_vulnerable("2.32.0", "<2.31.0") is False

    # Combined range >=2.0.0, <2.0.6
    assert VulnerabilityEngine.is_version_vulnerable("2.0.3", ">=2.0.0, <2.0.6") is True
    assert VulnerabilityEngine.is_version_vulnerable("1.9.9", ">=2.0.0, <2.0.6") is False
    assert VulnerabilityEngine.is_version_vulnerable("2.0.6", ">=2.0.0, <2.0.6") is False


def test_match_pypi_vulnerabilities():
    matches = VulnerabilityEngine.match_component("requests", "2.28.0", "pypi")
    assert len(matches) >= 1
    cve = matches[0]
    assert cve["cve_id"] == "CVE-2023-32681"
    assert cve["cvss_v3_score"] == 6.1
    assert cve["remediation_version"] == "2.31.0"


def test_match_npm_cisa_kev_vulnerability():
    matches = VulnerabilityEngine.match_component("lodash", "4.17.15", "npm")
    assert len(matches) >= 1
    cve = matches[0]
    assert cve["cve_id"] == "CVE-2020-8203"
    assert cve["cisa_kev"] is True
    assert cve["remediation_version"] == "4.17.21"


def test_match_cargo_prost_vulnerability():
    matches = VulnerabilityEngine.match_component("prost", "0.12.0", "cargo")
    assert len(matches) >= 1
    cve = matches[0]
    assert cve["cve_id"] == "CVE-2024-27308"
    assert cve["severity"] == "HIGH"


def test_match_golang_vulnerability():
    matches = VulnerabilityEngine.match_component("golang.org/x/net", "0.17.0", "golang")
    assert len(matches) >= 1
    cve = matches[0]
    assert cve["cve_id"] == "CVE-2023-45288"
    assert cve["cisa_kev"] is True


def test_secure_version_no_match():
    matches = VulnerabilityEngine.match_component("requests", "2.32.3", "pypi")
    assert len(matches) == 0
