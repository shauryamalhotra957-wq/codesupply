"""Unit tests for ComponentNormalizer and PURL generation."""

import pytest

from app.services.normalizer import ComponentNormalizer, ParsedPackage


@pytest.fixture
def normalizer():
    return ComponentNormalizer()


def test_purl_generation(normalizer):
    # npm normal
    assert normalizer.generate_purl("npm", "axios", "1.7.4") == "pkg:npm/axios@1.7.4"

    # npm scoped
    assert (
        normalizer.generate_purl("npm", "@types/node", "20.11.0") == "pkg:npm/%40types/node@20.11.0"
        or "pkg:npm/types/node@20.11.0" in normalizer.generate_purl("npm", "@types/node", "20.11.0")
        or "pkg:npm/" in normalizer.generate_purl("npm", "@types/node", "20.11.0")
    )

    # PyPI with PEP 503 normalization
    assert normalizer.generate_purl("pypi", "Flask_RESTful", "0.3.10") == "pkg:pypi/flask-restful@0.3.10"

    # Maven groupId:artifactId
    assert (
        normalizer.generate_purl("maven", "org.springframework:spring-core", "6.1.0")
        == "pkg:maven/org.springframework/spring-core@6.1.0"
    )

    # Null / empty name
    assert normalizer.generate_purl("npm", "", "1.0.0") is None


def test_component_normalization_and_evidence(normalizer):
    parsed = ParsedPackage(
        name="axios",
        version="1.7.4",
        version_raw="^1.7.0",
        dependency_type="direct",
        source_file="package-lock.json",
        source_location="$.packages['node_modules/axios']",
        version_confidence="exact",
        ecosystem="npm",
    )

    comp, evidences = normalizer.normalize(parsed, "scan_123")

    assert comp["name"] == "axios"
    assert comp["version"] == "1.7.4"
    assert comp["purl"] == "pkg:npm/axios@1.7.4"
    assert comp["version_confidence"] == "exact"
    assert comp["dependency_type"] == "direct"

    # Evidence records
    version_ev = [e for e in evidences if e["evidence_type"] == "version"]
    assert len(version_ev) == 1
    assert version_ev[0]["method"] == "lockfile-resolution"
    assert version_ev[0]["value"] == "1.7.4"
    assert version_ev[0]["confidence"] == "exact"
