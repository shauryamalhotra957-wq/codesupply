import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import DatabaseRepository

client = TestClient(app)


def test_demo_project_has_vulnerabilities_and_diff():
    # 1. Load python sample
    res_py = client.post("/api/projects/demo/python")
    assert res_py.status_code == 200
    py_proj = res_py.json()

    # 2. Query vulnerabilities endpoint
    res_vuln = client.get(f"/api/projects/{py_proj['id']}/vulnerabilities")
    assert res_vuln.status_code == 200
    vulns = res_vuln.json()
    assert isinstance(vulns, list)

    # 3. Load node sample and compare
    res_node = client.post("/api/projects/demo/node")
    assert res_node.status_code == 200
    node_proj = res_node.json()

    res_diff = client.get(f"/api/projects/{py_proj['id']}/compare/{node_proj['id']}")
    assert res_diff.status_code == 200
    diff_data = res_diff.json()
    assert "added_components" in diff_data
    assert "removed_components" in diff_data
    assert "version_changes" in diff_data
    assert "new_vulnerabilities" in diff_data
