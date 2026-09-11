from app.models.models import Component, Scan, VulnerabilityFinding
from app.services.report import ExecutiveReportGenerator


def test_executive_report_generation():
    scan = Scan(id="test_scan_report", filename="sample.zip", project_name="sample-project")
    components = [
        Component(
            id="c1",
            scan_id="test_scan_report",
            name="lodash",
            version="4.17.15",
            ecosystem="npm",
            dependency_type="direct",
            source_file="package.json",
            version_confidence="exact",
            normalized_name="lodash",
            risk_level="high",
        )
    ]
    vulns = [
        VulnerabilityFinding(
            id="v1",
            scan_id="test_scan_report",
            component_id="c1",
            vuln_id="GHSA-p6mc-m468-83gw",
            severity="high",
            summary="Prototype Pollution in lodash",
            source="osv",
            cvss_score=7.4,
        )
    ]

    generator = ExecutiveReportGenerator()
    html = generator.generate_html(scan, components, vulns)

    assert "<!DOCTYPE html>" in html
    assert "CodeSupply Executive Security Audit" in html
    assert "sample-project" in html
    assert "Prototype Pollution in lodash" in html
    assert "EO 14028" in html or "Executive Order 14028" in html
    assert "NTIA Minimum Elements" in html
