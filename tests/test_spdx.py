from scanner.normalization.normalizer import NormalizedComponent
from scanner.sbom.spdx_generator import SPDXGenerator


def test_spdx_generation():
    components = [
        NormalizedComponent(
            name="fastapi",
            version="0.110.0",
            ecosystem="pypi",
            direct=True,
            source_file="requirements.txt",
            purl="pkg:pypi/fastapi@0.110.0",
            license="MIT",
        ),
        NormalizedComponent(
            name="serde",
            version="1.0.197",
            ecosystem="cargo",
            direct=True,
            source_file="Cargo.toml",
            purl="pkg:cargo/serde@1.0.197",
            license="MIT",
        ),
        NormalizedComponent(
            name="github.com/gin-gonic/gin",
            version="1.9.1",
            ecosystem="golang",
            direct=False,
            source_file="go.mod",
            purl="pkg:golang/github.com/gin-gonic/gin@1.9.1",
            integrity="sha256-dummyhash",
        ),
    ]

    spdx = SPDXGenerator.generate_sbom(
        project_name="TestMultiEcosystemApp",
        components=components,
        project_version="2.0.0",
    )

    assert spdx["spdxVersion"] == "SPDX-2.3"
    assert spdx["dataLicense"] == "CC0-1.0"
    assert spdx["SPDXID"] == "SPDXRef-DOCUMENT"
    assert len(spdx["packages"]) == 4  # 1 root + 3 components
    assert "creationInfo" in spdx

    root_pkg = next(p for p in spdx["packages"] if p["SPDXID"] == "SPDXRef-Package-Root")
    assert root_pkg["name"] == "TestMultiEcosystemApp"
    assert root_pkg["versionInfo"] == "2.0.0"

    fastapi_pkg = next(p for p in spdx["packages"] if "pypi-fastapi" in p["SPDXID"])
    assert fastapi_pkg["name"] == "fastapi"
    assert fastapi_pkg["versionInfo"] == "0.110.0"
    assert fastapi_pkg["externalRefs"][0]["referenceLocator"] == "pkg:pypi/fastapi@0.110.0"

    # Verify relationships
    depends_on = [r for r in spdx["relationships"] if r["relationshipType"] == "DEPENDS_ON"]
    assert len(depends_on) == 2  # 2 direct components (fastapi & serde)
