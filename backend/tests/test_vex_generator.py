"""Unit tests for CycloneDX 1.7 VEX and OpenVEX generator."""

from app.models.models import Component, Scan, VulnerabilityFinding
from app.sbom.vex import VEXGenerator


def test_cyclonedx_vex_generation():
    scan = Scan(id="scan_vex_123", filename="test.zip", project_name="secure-api")
    comp1 = Component(
        id="comp_1",
        scan_id="scan_vex_123",
        name="lodash",
        version="4.17.15",
        ecosystem="npm",
        purl="pkg:npm/lodash@4.17.15",
    )
    comp2 = Component(
        id="comp_2",
        scan_id="scan_vex_123",
        name="requests",
        version="2.25.0",
        ecosystem="pypi",
        purl="pkg:pypi/requests@2.25.0",
    )
    components = [comp1, comp2]

    vulns = [
        VulnerabilityFinding(
            id="vf_1",
            scan_id="scan_vex_123",
            component_id="comp_1",
            vuln_id="GHSA-p6mc-m468-83gw",
            summary="Prototype pollution in lodash",
            severity="high",
            cvss_score=7.4,
            cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
            fixed_version="4.17.21",
            references=["https://github.com/advisories/GHSA-p6mc-m468-83gw"],
        ),
        VulnerabilityFinding(
            id="vf_2",
            scan_id="scan_vex_123",
            component_id="comp_2",
            vuln_id="PYSEC-2023-1234",
            summary="Information disclosure in requests",
            severity="medium",
            cvss_score=None,
            fixed_version=None,
            references=[],
        ),
    ]

    vex_doc = VEXGenerator.generate_cyclonedx_vex(scan, components, vulns)

    assert vex_doc["bomFormat"] == "CycloneDX"
    assert vex_doc["specVersion"] == "1.7"
    assert "serialNumber" in vex_doc
    assert vex_doc["metadata"]["component"]["name"] == "secure-api"

    v_entries = vex_doc["vulnerabilities"]
    assert len(v_entries) == 2

    # Verify first vuln (with fix & CVSS)
    v1 = v_entries[0]
    assert v1["id"] == "GHSA-p6mc-m468-83gw"
    assert v1["analysis"]["state"] == "exploitable"
    assert v1["analysis"]["response"] == ["update"]
    assert v1["ratings"][0]["score"] == 7.4
    assert v1["ratings"][0]["method"] == "CVSSv31"
    assert v1["affects"][0]["ref"] == "pkg:npm/lodash@4.17.15"
    assert len(v1["advisories"]) == 1

    # Verify second vuln (unfixed, in_triage)
    v2 = v_entries[1]
    assert v2["id"] == "PYSEC-2023-1234"
    assert v2["analysis"]["state"] == "in_triage"
    assert v2["analysis"]["response"] == ["workaround_available"]
    assert v2["ratings"][0]["severity"] == "medium"
    assert v2["affects"][0]["ref"] == "pkg:pypi/requests@2.25.0"


def test_openvex_generation():
    scan = Scan(id="scan_openvex_123", filename="test.zip", project_name="secure-api")
    comp1 = Component(
        id="comp_1",
        scan_id="scan_openvex_123",
        name="lodash",
        version="4.17.15",
        ecosystem="npm",
        purl="pkg:npm/lodash@4.17.15",
    )
    components = [comp1]

    vulns = [
        VulnerabilityFinding(
            id="vf_1",
            scan_id="scan_openvex_123",
            component_id="comp_1",
            vuln_id="GHSA-p6mc-m468-83gw",
            summary="Prototype pollution",
            severity="high",
            fixed_version="4.17.21",
        ),
    ]

    openvex = VEXGenerator.generate_openvex(scan, components, vulns)
    assert openvex["@context"] == "https://openvex.dev/ns/v0.2.0"
    assert openvex["author"] == "CodeSupply VEX Engine (SIH1449)"
    assert len(openvex["statements"]) == 1

    stmt = openvex["statements"][0]
    assert stmt["vulnerability"]["name"] == "GHSA-p6mc-m468-83gw"
    assert stmt["products"] == ["pkg:npm/lodash@4.17.15"]
    assert stmt["status"] == "fixed"
    assert "Upgrade to version 4.17.21" in stmt["action_statement"]
