"""Tests for OSV advisory response parsing using deterministic fixtures."""

import json
from pathlib import Path

from app.core.config import Settings
from app.models.models import Component
from app.workers.runner import ScanWorker


def test_osv_fixtures_exist():
    fixtures_dir = Path(__file__).parent / "fixtures"
    assert (fixtures_dir / "osv_response_no_vulns.json").exists()
    assert (fixtures_dir / "osv_response_lodash_vuln.json").exists()
    assert (fixtures_dir / "osv_batch_response.json").exists()


def test_osv_finding_extraction():
    fixtures_dir = Path(__file__).parent / "fixtures"
    with open(fixtures_dir / "osv_response_lodash_vuln.json") as f:
        data = json.load(f)

    vuln_data = data["results"][0]["vulns"][0]

    worker = ScanWorker(Settings())
    comp = Component(
        id="comp_lodash",
        name="lodash",
        version="4.17.20",
        ecosystem="npm",
        dependency_type="direct",
        source_file="package-lock.json",
    )

    finding = worker._create_finding(comp, vuln_data, "scan_test")

    assert finding.vuln_id == "GHSA-jf85-cpcp-j695"
    assert "Prototype Pollution" in finding.summary
    assert finding.component_id == "comp_lodash"
    assert finding.fixed_version == "4.17.20" or finding.fixed_version is not None
    assert finding.source == "osv"
