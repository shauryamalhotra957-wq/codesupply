"""Unit tests for CycloneDX 1.7 SBOM generation and schema validation."""

from app.models.models import Component, DependencyEdge, Scan
from app.sbom.generator import CycloneDXGenerator
from app.sbom.validator import SBOMValidator


def test_cyclonedx_generation_and_validation():
    generator = CycloneDXGenerator()
    validator = SBOMValidator()

    scan = Scan(id="scan_abc123", filename="my-project.zip", project_name="my-project")
    comp1 = Component(
        id="comp_1",
        name="axios",
        version="1.7.4",
        ecosystem="npm",
        purl="pkg:npm/axios@1.7.4",
        dependency_type="direct",
        source_file="package-lock.json",
    )
    comp2 = Component(
        id="comp_2",
        name="follow-redirects",
        version="1.15.6",
        ecosystem="npm",
        purl="pkg:npm/follow-redirects@1.15.6",
        dependency_type="transitive",
        source_file="package-lock.json",
    )
    edge = DependencyEdge(
        id="edge_1",
        source_component_id="comp_1",
        target_component_id="comp_2",
        relationship_type="DEPENDS_ON",
        confidence="high",
        source_file="package-lock.json",
        evidence_method="observed-lockfile-edge",
    )

    sbom = generator.generate(scan, [comp1, comp2], [edge])

    # Assert standard CycloneDX 1.7 structure
    assert sbom["bomFormat"] == "CycloneDX"
    assert sbom["specVersion"] == "1.7"
    assert sbom["serialNumber"].startswith("urn:uuid:")
    assert len(sbom["components"]) == 2
    assert len(sbom["dependencies"]) == 1

    # Validate with validator
    validation = validator.validate(sbom)
    assert validation.is_valid is True
    assert len(validation.errors) == 0


def test_sbom_validation_rejects_invalid():
    validator = SBOMValidator()

    # Missing specVersion
    invalid_sbom = {
        "bomFormat": "CycloneDX",
        "components": [{"type": "library", "name": "foo"}],
    }
    val = validator.validate(invalid_sbom)
    assert val.is_valid is False
    assert any("specVersion" in e for e in val.errors)

    # Invalid PURL prefix
    invalid_purl = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.7",
        "components": [{"type": "library", "name": "foo", "purl": "invalid-purl-format"}],
    }
    val2 = validator.validate(invalid_purl)
    assert val2.is_valid is False
    assert any("purl" in e for e in val2.errors)
