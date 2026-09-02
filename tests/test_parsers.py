from pathlib import Path
import pytest

from scanner.parsers.python_parser import PythonParser
from scanner.parsers.node_parser import NodeParser


def test_python_requirements_parser(tmp_path: Path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text(
        """
        # Top comment
        fastapi==0.110.0
        uvicorn>=0.28.0,<0.30.0
        requests
        pytz~=2024.1
        celery[redis]==5.3.6 ; sys_platform == 'linux'
        git+https://github.com/org/pkg.git#egg=custom-pkg
        -r other.txt
        """,
        encoding="utf-8",
    )

    parser = PythonParser()
    assert parser.can_parse("requirements.txt") is True
    assert parser.can_parse("requirements-prod.txt") is True
    assert parser.can_parse("pyproject.toml") is True
    assert parser.can_parse("package.json") is False

    deps = parser.parse(req_file, "requirements.txt")
    names = {d.name: d for d in deps}

    assert "fastapi" in names
    assert names["fastapi"].version == "0.110.0"
    assert names["fastapi"].specifier == "==0.110.0"
    assert names["fastapi"].direct is True

    assert "uvicorn" in names
    assert names["uvicorn"].version is None
    assert ">=0.28.0" in names["uvicorn"].specifier

    assert "requests" in names
    assert names["requests"].version is None

    assert "celery" in names
    assert names["celery"].version == "5.3.6"
    assert names["celery"].metadata.get("extras") == ["redis"]

    assert "custom-pkg" in names
    assert names["custom-pkg"].metadata.get("url_install") is not None


def test_python_pyproject_toml_parser(tmp_path: Path):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(
        """
        [project]
        name = "test-project"
        version = "0.1.0"
        dependencies = [
            "flask==3.0.2",
            "pydantic>=2.6.0"
        ]

        [project.optional-dependencies]
        dev = [
            "pytest==8.1.1"
        ]
        """,
        encoding="utf-8",
    )

    parser = PythonParser()
    deps = parser.parse(toml_file, "pyproject.toml")
    names = {d.name: d for d in deps}

    assert "flask" in names
    assert names["flask"].version == "3.0.2"
    assert names["flask"].scope == "required"

    assert "pytest" in names
    assert names["pytest"].version == "8.1.1"
    assert names["pytest"].scope == "optional"


def test_node_package_json_parser(tmp_path: Path):
    pkg_file = tmp_path / "package.json"
    pkg_file.write_text(
        """
        {
            "name": "test-node",
            "dependencies": {
                "express": "^4.19.2",
                "lodash": "4.17.21"
            },
            "devDependencies": {
                "jest": "~29.7.0"
            }
        }
        """,
        encoding="utf-8",
    )

    parser = NodeParser()
    assert parser.can_parse("package.json") is True
    assert parser.can_parse("package-lock.json") is True

    deps = parser.parse(pkg_file, "package.json")
    names = {d.name: d for d in deps}

    assert "express" in names
    assert names["express"].specifier == "^4.19.2"
    assert names["express"].scope == "required"
    assert names["express"].direct is True

    assert "lodash" in names
    assert names["lodash"].version == "4.17.21"

    assert "jest" in names
    assert names["jest"].scope == "dev"


def test_node_package_lock_v3_parser(tmp_path: Path):
    lock_file = tmp_path / "package-lock.json"
    lock_file.write_text(
        """
        {
            "name": "test-app",
            "version": "1.0.0",
            "lockfileVersion": 3,
            "packages": {
                "": {
                    "dependencies": {
                        "express": "^4.19.2"
                    }
                },
                "node_modules/express": {
                    "version": "4.19.2",
                    "resolved": "https://registry.npmjs.org/express/-/express-4.19.2.tgz",
                    "integrity": "sha512-test-hash",
                    "license": "MIT",
                    "dependencies": {
                        "accepts": "~1.3.8"
                    }
                },
                "node_modules/accepts": {
                    "version": "1.3.8",
                    "resolved": "https://registry.npmjs.org/accepts/-/accepts-1.3.8.tgz",
                    "integrity": "sha512-accepts-hash",
                    "license": "MIT"
                }
            }
        }
        """,
        encoding="utf-8",
    )

    parser = NodeParser()
    deps = parser.parse(lock_file, "package-lock.json")
    names = {d.name: d for d in deps}

    assert "express" in names
    assert names["express"].version == "4.19.2"
    assert names["express"].direct is True
    assert names["express"].integrity == "sha512-test-hash"
    assert "accepts" in names["express"].dependencies

    assert "accepts" in names
    assert names["accepts"].version == "1.3.8"
    assert names["accepts"].direct is False
