from fastapi.testclient import TestClient
from backend.main import app
from scanner.sbom.sarif_generator import SarifGenerator
from backend.services.license_policy_service import LicensePolicyService

client = TestClient(app)


def test_sarif_generator_structure():
    findings = [
        {
            "component_name": "requests",
            "severity": "high",
            "category": "vulnerability",
            "title": "CVE-2023-32681 Information Disclosure",
            "evidence": "Fixed in 2.31.0",
            "recommendation": "Upgrade requests to >= 2.31.0",
            "source_file": "requirements.txt",
        }
    ]
    components = [
        {
            "name": "requests",
            "version": "2.28.0",
            "purl": "pkg:pypi/requests@2.28.0",
            "source_file": "requirements.txt",
        }
    ]

    sarif = SarifGenerator.generate_sarif("TestProject", findings, components)
    assert sarif["version"] == "2.1.0"
    assert len(sarif["runs"]) == 1
    run = sarif["runs"][0]
    assert run["tool"]["driver"]["name"] == "CodeSupply"
    assert len(run["results"]) == 1
    res = run["results"][0]
    assert res["level"] == "error"
    assert res["ruleId"] == "CS-VULNERABILITY"
    assert "requests" in res["message"]["text"]


def test_license_policy_service():
    components = [
        {"name": "fastapi", "version": "0.110.0", "license": "MIT"},
        {"name": "urllib3", "version": "1.26.5", "license": "Apache-2.0"},
        {"name": "gpl-tool", "version": "1.0.0", "license": "GPL-3.0"},
        {"name": "mystery-lib", "version": "0.1.0", "license": None},
    ]

    eval_result = LicensePolicyService.evaluate_project_licenses(components)
    dist = eval_result["distribution"]
    assert dist["permissive"] == 2
    assert dist["strong_copyleft"] == 1
    assert dist["unknown"] == 1
    assert len(eval_result["risk_flags"]) == 2  # 1 strong copyleft, 1 unknown
    assert eval_result["compliance_score"] < 100


def test_sarif_and_license_api_endpoints():
    # Load demo python project
    res = client.post("/api/projects/demo/python-project")
    assert res.status_code == 200
    project_id = res.json()["id"]

    # Test SARIF endpoint
    sarif_res = client.get(f"/api/projects/{project_id}/export/sarif")
    assert sarif_res.status_code == 200
    sarif_data = sarif_res.json()
    assert sarif_data["version"] == "2.1.0"
    assert len(sarif_data["runs"]) > 0

    # Test Licenses endpoint
    lic_res = client.get(f"/api/projects/{project_id}/licenses")
    assert lic_res.status_code == 200
    lic_data = lic_res.json()
    assert "compliance_score" in lic_data
    assert "distribution" in lic_data
    assert "risk_flags" in lic_data
