from scanner.normalization.normalizer import DependencyNormalizer
from scanner.parsers.base import ParsedDependency


def test_purl_generation():
    assert DependencyNormalizer.generate_purl("requests", "2.31.0", "pypi") == "pkg:pypi/requests@2.31.0"
    assert DependencyNormalizer.generate_purl("Requests", "2.31.0", "pypi") == "pkg:pypi/requests@2.31.0"
    assert DependencyNormalizer.generate_purl("Flask-Cors", "4.0.0", "pypi") == "pkg:pypi/flask-cors@4.0.0"
    assert DependencyNormalizer.generate_purl("express", "4.19.2", "npm") == "pkg:npm/express@4.19.2"
    assert DependencyNormalizer.generate_purl("@types/node", "20.11.0", "npm") == "pkg:npm/%40types/node@20.11.0"
    assert DependencyNormalizer.generate_purl("unpinned-pkg", None, "pypi") == "pkg:pypi/unpinned-pkg"


def test_normalizer_merging():
    raw_deps = [
        # In package.json (direct, range specifier)
        ParsedDependency(
            name="express",
            version=None,
            specifier="^4.19.2",
            ecosystem="npm",
            direct=True,
            source_file="package.json",
        ),
        # In package-lock.json (exact pinned version, transitive links)
        ParsedDependency(
            name="express",
            version="4.19.2",
            specifier="==4.19.2",
            ecosystem="npm",
            direct=True,
            source_file="package-lock.json",
            license="MIT",
            integrity="sha512-hash123",
            dependencies=["accepts", "cookie"],
        ),
    ]

    normalized = DependencyNormalizer.normalize_list(raw_deps)
    assert len(normalized) == 1
    comp = normalized[0]

    assert comp.name == "express"
    assert comp.version == "4.19.2"
    assert comp.direct is True
    assert comp.purl == "pkg:npm/express@4.19.2"
    assert comp.license == "MIT"
    assert comp.integrity == "sha512-hash123"
    assert "package.json" in comp.source_files
    assert "package-lock.json" in comp.source_files
    assert "accepts" in comp.dependencies
