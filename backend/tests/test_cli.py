from pathlib import Path

from app.cli import scan_directory


def test_cli_scan_sample_project(tmp_path):
    # Test scan directory with demo project
    demo_dir = Path(__file__).resolve().parent.parent.parent / "sample-projects" / "demo-project"
    if not demo_dir.exists():
        return

    out_sbom = tmp_path / "sbom.json"
    scan_directory(demo_dir, export_sbom=str(out_sbom), sbom_format="cyclonedx")
    assert out_sbom.exists()
    assert '"bomFormat": "CycloneDX"' in out_sbom.read_text(encoding="utf-8")
