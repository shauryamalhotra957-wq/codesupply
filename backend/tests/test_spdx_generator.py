from app.models.models import Component, DependencyEdge, Scan
from app.sbom.spdx import SPDX23Generator


def test_spdx_generator_structure():
    scan = Scan(id="test_scan_123", filename="my-app.zip", project_name="my-app")
    components = [
        Component(
            id="comp_1",
            scan_id="test_scan_123",
            name="express",
            version="4.18.2",
            ecosystem="npm",
            dependency_type="direct",
            source_file="package.json",
            version_confidence="exact",
            purl="pkg:npm/express@4.18.2",
            license="MIT",
            normalized_name="express",
            risk_level="none",
        ),
        Component(
            id="comp_2",
            scan_id="test_scan_123",
            name="debug",
            version="2.6.9",
            ecosystem="npm",
            dependency_type="transitive",
            source_file="package-lock.json",
            version_confidence="exact",
            purl="pkg:npm/debug@2.6.9",
            license="MIT",
            normalized_name="debug",
            risk_level="none",
        ),
    ]
    edges = [
        DependencyEdge(
            id="edge_1",
            scan_id="test_scan_123",
            source_component_id="comp_1",
            target_component_id="comp_2",
            relationship_type="depends_on",
            confidence="high",
            source_file="package-lock.json",
            evidence_method="lockfile_v3",
        )
    ]

    generator = SPDX23Generator()
    doc = generator.generate(scan, components, edges)

    assert doc["spdxVersion"] == "SPDX-2.3"
    assert doc["dataLicense"] == "CC0-1.0"
    assert doc["SPDXID"] == "SPDXRef-DOCUMENT"
    assert "creationInfo" in doc
    assert len(doc["packages"]) == 3  # Root + 2 components
    assert doc["packages"][0]["SPDXID"] == "SPDXRef-Package-Root"
    assert doc["packages"][1]["name"] == "express"
    assert doc["packages"][1]["externalRefs"][0]["referenceLocator"] == "pkg:npm/express@4.18.2"

    # Verify relationships
    assert any(
        r["relationshipType"] == "DESCRIBES" and r["relatedSpdxElement"] == "SPDXRef-Package-Root"
        for r in doc["relationships"]
    )
    assert any(
        r["relationshipType"] == "DEPENDS_ON" and r["spdxElementId"] == "SPDXRef-Package-Root"
        for r in doc["relationships"]
    )
