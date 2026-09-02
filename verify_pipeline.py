from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
samples_dir = Path(__file__).resolve().parent / "samples"

print("--- 1. Testing Health Endpoint ---")
h_res = client.get("/health")
print("Health:", h_res.json())

for sample_name in ["python-project", "node-project", "mixed-project", "broken-project"]:
    print(f"\n--- Testing Upload for {sample_name}.zip ---")
    zip_path = samples_dir / f"{sample_name}.zip"
    with open(zip_path, "rb") as f:
        upload_res = client.post("/api/projects/upload", files={"file": (zip_path.name, f, "application/zip")})
    assert upload_res.status_code == 200, upload_res.text
    proj = upload_res.json()
    proj_id = proj["id"]
    print(f"  Project ID: {proj_id}")
    print(f"  Name: {proj['name']}")
    print(f"  Ecosystems: {proj['ecosystems']}")
    print(f"  Total Components: {proj['total_components']} (Direct: {proj['direct_count']}, Transitive: {proj['transitive_count']})")
    print(f"  Findings Count: {proj['findings_count']} (High: {proj['high_findings']}, Med: {proj['medium_findings']}, Low: {proj['low_findings']})")

    # Check CycloneDX
    sbom_res = client.get(f"/api/projects/{proj_id}/sbom")
    assert sbom_res.status_code == 200
    sbom = sbom_res.json()
    print(f"  CycloneDX Spec: {sbom['specVersion']}, Serial: {sbom['serialNumber']}")
    print(f"  CycloneDX Components Count: {len(sbom['components'])}")
    print(f"  CycloneDX Dependencies Count: {len(sbom['dependencies'])}")

    # Check Graph
    graph_res = client.get(f"/api/projects/{proj_id}/graph")
    assert graph_res.status_code == 200
    graph = graph_res.json()
    print(f"  Graph Nodes: {graph['total_nodes']}, Graph Edges: {graph['total_edges']}")

    # Check PDF Report
    pdf_res = client.get(f"/api/projects/{proj_id}/report")
    assert pdf_res.status_code == 200
    print(f"  PDF Audit Report: {len(pdf_res.content)} bytes")

    # Check CSV Export
    csv_res = client.get(f"/api/projects/{proj_id}/export/csv")
    assert csv_res.status_code == 200
    print(f"  CSV Component Inventory: {len(csv_res.content)} bytes")

print("\n[SUCCESS] ALL 4 REAL SAMPLE ZIP UPLOADS AND PIPELINE CHECKS PASSED PERFECTLY!")
