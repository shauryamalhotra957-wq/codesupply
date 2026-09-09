"""Tests for CVSS v3 base score computation and severity extraction."""

from app.core.config import get_settings
from app.workers.runner import ScanWorker


def test_cvss3_base_score_computation():
    """Verify CVSS v3.1 standard vector calculations match specification."""
    # Log4j / Critical (Score: 10.0)
    # AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H
    score = ScanWorker._compute_cvss3_base_score("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H")
    assert score == 10.0
    assert ScanWorker._score_to_severity(score) == "critical"

    # Typical Remote Code Execution / Critical (Score: 9.8)
    # AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
    score = ScanWorker._compute_cvss3_base_score("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
    assert score == 9.8
    assert ScanWorker._score_to_severity(score) == "critical"

    # Authenticated High (Score: 8.8)
    # AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H
    score = ScanWorker._compute_cvss3_base_score("CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H")
    assert score == 8.8
    assert ScanWorker._score_to_severity(score) == "high"

    # Stored XSS / Medium (Score: 5.4)
    # AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N
    score = ScanWorker._compute_cvss3_base_score("CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N")
    assert score == 5.4
    assert ScanWorker._score_to_severity(score) == "medium"

    # Local Info Disclosure / Low (Score: 3.3)
    # AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N
    score = ScanWorker._compute_cvss3_base_score("CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N")
    assert score == 3.3
    assert ScanWorker._score_to_severity(score) == "low"


def test_invalid_cvss_vector_returns_none():
    assert ScanWorker._compute_cvss3_base_score("invalid-vector") is None
    assert ScanWorker._compute_cvss3_base_score("") is None


def test_severity_extraction_strategies():
    worker = ScanWorker(get_settings())

    # Strategy 1: CVSS_V3 in severity list
    vuln_cvss = {
        "id": "GHSA-test-1",
        "severity": [{"type": "CVSS_V3", "score": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"}],
    }
    sev, score, vector = worker._extract_severity(vuln_cvss)
    assert sev == "critical"
    assert score == 9.8
    assert "AV:N" in vector

    # Strategy 2: database_specific.severity
    vuln_db_specific = {
        "id": "GHSA-test-2",
        "database_specific": {"severity": "HIGH"},
    }
    sev, score, vector = worker._extract_severity(vuln_db_specific)
    assert sev == "high"

    # Strategy 2b: database_specific with MODERATE
    vuln_moderate = {
        "id": "GHSA-test-3",
        "database_specific": {"severity": "MODERATE"},
    }
    sev, score, vector = worker._extract_severity(vuln_moderate)
    assert sev == "medium"

    # Strategy 4: Fallback to alias CVE
    vuln_cve = {
        "id": "PYSEC-2021-123",
        "aliases": ["CVE-2021-12345"],
    }
    sev, score, vector = worker._extract_severity(vuln_cve)
    assert sev == "medium"
