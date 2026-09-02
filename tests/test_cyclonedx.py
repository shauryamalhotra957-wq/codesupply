from scanner.normalization.normalizer import NormalizedComponent
from scanner.sbom.cyclonedx_generator import CycloneDXGenerator


def test_cyclonedx_generation():
    components = [
        NormalizedComponent(
            name="express",
            version="4.19.2",
            ecosystem="npm",
            direct=True,
            purl="pkg:npm/express@4.19.2",
            source_file="package.json",
            license="MIT",
            integrity="sha512-mockhash",
            dependencies=["accepts"],
        ),
        NormalizedComponent(
            name="accepts",
            version="1.3.8",
            ecosystem="npm",
            direct=False,
            purl="pkg:npm/accepts@1.3.8",
            source_file="package-lock.json",
            license="MIT",
        ),
    ]

    sbom = CycloneDXGenerator.generate_sbom(
        project_name="demo-node-app",
        components=components,
    )

    assert sbom["bomFormat"] == "CycloneDX"
    assert sbom["specVersion"] == "1.5"
    assert sbom["serialNumber"].startswith("urn:uuid:")
    assert sbom["version"] == 1
    assert sbom["metadata"]["component"]["name"] == "demo-node-app"
    assert len(sbom["components"]) == 2

    comp_map = {c["name"]: c for c in sbom["components"]}
    assert "express" in comp_map
    assert comp_map["express"]["purl"] == "pkg:npm/express@4.19.2"
    assert comp_map["express"]["licenses"][0]["license"]["name"] == "MIT"
    assert comp_map["express"]["hashes"][0]["alg"] == "SHA-512"

    assert len(sbom["dependencies"]) >= 1
