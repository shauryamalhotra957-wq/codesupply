"""Unit tests for Python requirements.txt and pyproject.toml parser."""

import pytest

from app.scanners.python.parser import PythonParser


@pytest.fixture
def parser():
    return PythonParser()


def test_parse_requirements_txt_pinned_and_ranges(parser):
    content = """
    # Primary web framework
    flask==3.0.3
    requests>=2.31.0
    urllib3
    Django~=5.0
    pydantic>=2.0,<3.0

    # Flags and includes to ignore
    -r other-requirements.txt
    --extra-index-url https://custom.pypi.org/simple
    """

    packages = parser.parse_requirements_txt(content, "requirements.txt")
    pkg_map = {p.name: p for p in packages}

    # Pinned version
    assert "flask" in pkg_map
    assert pkg_map["flask"].version == "3.0.3"
    assert pkg_map["flask"].version_confidence == "exact"
    assert pkg_map["flask"].dependency_type == "direct"

    # Declared range
    assert "requests" in pkg_map
    assert pkg_map["requests"].version_confidence == "declared_range"
    assert pkg_map["requests"].version is None or pkg_map["requests"].version_confidence != "exact"

    # Unpinned package -> unknown version
    assert "urllib3" in pkg_map
    assert pkg_map["urllib3"].version is None
    assert pkg_map["urllib3"].version_confidence == "unknown"

    # Compatible release
    assert "Django" in pkg_map or "django" in pkg_map
    django_pkg = pkg_map.get("Django") or pkg_map.get("django")
    assert django_pkg.version_confidence == "declared_range"

    # Bounded range
    assert "pydantic" in pkg_map
    assert pkg_map["pydantic"].version_confidence == "declared_range"


def test_parse_pyproject_toml(parser):
    content = """
    [project]
    name = "demo-service"
    version = "0.1.0"
    dependencies = [
        "fastapi>=0.100.0",
        "httpx==0.27.0"
    ]

    [project.optional-dependencies]
    test = [
        "pytest>=8.0.0"
    ]
    """

    packages = parser.parse_pyproject_toml(content, "pyproject.toml")
    pkg_map = {p.name: p for p in packages}

    assert "fastapi" in pkg_map
    assert pkg_map["fastapi"].dependency_type == "direct"
    assert pkg_map["fastapi"].version_confidence == "declared_range"

    assert "httpx" in pkg_map
    assert pkg_map["httpx"].version == "0.27.0"
    assert pkg_map["httpx"].version_confidence == "exact"

    assert "pytest" in pkg_map
    assert pkg_map["pytest"].dependency_type == "optional"


def test_parse_malformed_requirements(parser):
    content = """
    valid-pkg==1.0.0
    !!!not a valid requirement specifier 123
    another-pkg>=2.0
    """
    packages = parser.parse_requirements_txt(content, "requirements.txt")
    names = [p.name for p in packages]
    assert "valid-pkg" in names
    assert "another-pkg" in names
