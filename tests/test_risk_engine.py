from backend.services.risk_engine import RiskEngine
from backend.services.risk_explanation_service import RiskExplanationService
from scanner.normalization.normalizer import NormalizedComponent
from scanner.parsers.base import ParsedDependency


def test_risk_engine_anomalies():
    raw_deps = [
        # Unpinned package
        ParsedDependency(
            name="requests",
            version=None,
            specifier="",
            ecosystem="pypi",
            direct=True,
            source_file="requirements.txt",
        ),
        # Duplicate with conflicting specifiers
        ParsedDependency(
            name="urllib3",
            version=None,
            specifier=">=2.0.0",
            ecosystem="pypi",
            direct=True,
            source_file="requirements.txt",
        ),
        ParsedDependency(
            name="urllib3",
            version=None,
            specifier="<1.27.0",
            ecosystem="pypi",
            direct=True,
            source_file="extra-requirements.txt",
        ),
        # Wildcard package
        ParsedDependency(
            name="lodash",
            version=None,
            specifier="*",
            ecosystem="npm",
            direct=True,
            source_file="package.json",
        ),
        # Deprecated package
        ParsedDependency(
            name="pycrypto",
            version="2.6.1",
            specifier="==2.6.1",
            ecosystem="pypi",
            direct=True,
            source_file="requirements.txt",
        ),
    ]

    components = [
        NormalizedComponent(
            name="requests",
            version=None,
            raw_specifier="",
            ecosystem="pypi",
            direct=True,
            source_file="requirements.txt",
            purl="pkg:pypi/requests",
        ),
        NormalizedComponent(
            name="lodash",
            version=None,
            raw_specifier="*",
            ecosystem="npm",
            direct=True,
            source_file="package.json",
            purl="pkg:npm/lodash",
        ),
        NormalizedComponent(
            name="pycrypto",
            version="2.6.1",
            raw_specifier="==2.6.1",
            ecosystem="pypi",
            direct=True,
            source_file="requirements.txt",
            purl="pkg:pypi/pycrypto@2.6.1",
        ),
    ]

    findings = RiskEngine.analyze(raw_deps, components)
    categories = {f.category for f in findings}
    titles = [f.title for f in findings]

    assert "Version Pinning" in categories
    assert "Duplicate" in categories
    assert "Conflict" in categories
    assert "Hygiene" in categories

    # Test Risk Explanation Service
    service = RiskExplanationService()
    enriched = service.enrich_findings(findings)

    for f in enriched:
        assert len(f.explanation) > 10
        assert len(f.recommendation) > 10
