from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from backend.main import app

client = TestClient(app)


def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "pypi" in data["supported_ecosystems"]


def test_load_sample_demo_python():
    res = client.post("/api/projects/demo/python-project")
    assert res.status_code == 200
    data = res.json()
    assert "id" in data
    assert data["total_components"] > 0
    assert "pypi" in data["ecosystems"]

    project_id = data["id"]

    # Test components endpoint
    comp_res = client.get(f"/api/projects/{project_id}/components")
    assert comp_res.status_code == 200
    comps = comp_res.json()
    assert len(comps) == data["total_components"]

    # Test graph endpoint
    graph_res = client.get(f"/api/projects/{project_id}/graph")
    assert graph_res.status_code == 200
    graph = graph_res.json()
    assert "react_flow" in graph
    assert len(graph["react_flow"]["nodes"]) > 0

    # Test findings endpoint
    findings_res = client.get(f"/api/projects/{project_id}/findings")
    assert findings_res.status_code == 200

    # Test CycloneDX endpoint
    sbom_res = client.get(f"/api/projects/{project_id}/sbom")
    assert sbom_res.status_code == 200
    sbom = sbom_res.json()
    assert sbom["bomFormat"] == "CycloneDX"

    # Test CSV export
    csv_res = client.get(f"/api/projects/{project_id}/export/csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]

    # Test PDF report export
    pdf_res = client.get(f"/api/projects/{project_id}/report")
    assert pdf_res.status_code == 200
    assert "application/pdf" in pdf_res.headers["content-type"]
    assert len(pdf_res.content) > 500


def test_load_sample_demo_broken():
    res = client.post("/api/projects/demo/broken-project")
    assert res.status_code == 200
    data = res.json()
    assert data["findings_count"] > 0
    assert data["high_findings"] > 0

    # Check that findings have explanations and recommendations
    findings_res = client.get(f"/api/projects/{data['id']}/findings")
    assert findings_res.status_code == 200
    findings = findings_res.json()
    assert len(findings) > 0
    assert all(len(f["explanation"]) > 0 for f in findings)
    assert all(len(f["recommendation"]) > 0 for f in findings)
