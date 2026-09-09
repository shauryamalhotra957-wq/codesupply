"""Unit tests for npm package.json and package-lock.json parser."""

import json

import pytest

from app.scanners.npm.parser import NpmParser


@pytest.fixture
def parser():
    return NpmParser()


def test_parse_package_json_dependencies(parser):
    content = json.dumps(
        {
            "name": "my-app",
            "version": "1.0.0",
            "dependencies": {"express": "^4.18.2", "lodash": "4.17.21"},
            "devDependencies": {"jest": "~29.7.0"},
            "peerDependencies": {"react": ">=18.0.0"},
            "optionalDependencies": {"fsevents": "^2.3.2"},
        }
    )

    packages, relationships = parser.parse_package_json(content, "package.json")

    pkg_map = {p.name: p for p in packages}
    assert "express" in pkg_map
    assert pkg_map["express"].version_raw == "^4.18.2"
    assert pkg_map["express"].version_confidence == "declared_range"
    assert pkg_map["express"].dependency_type == "direct"

    # Exact in package.json
    assert "lodash" in pkg_map
    assert pkg_map["lodash"].version == "4.17.21"
    assert pkg_map["lodash"].version_confidence == "exact"

    assert "jest" in pkg_map
    assert pkg_map["jest"].dependency_type == "dev"

    assert "react" in pkg_map
    assert pkg_map["react"].dependency_type == "peer"

    assert "fsevents" in pkg_map
    assert pkg_map["fsevents"].dependency_type == "optional"

    # Check relationships
    assert any(r.target_name == "express" for r in relationships)


def test_parse_scoped_npm_package(parser):
    content = json.dumps({"name": "scoped-test", "dependencies": {"@types/node": "^20.0.0"}})
    packages, _ = parser.parse_package_json(content, "package.json")
    assert len(packages) == 1
    assert packages[0].name == "@types/node"
    assert packages[0].ecosystem == "npm"


def test_parse_package_lock_v3(parser):
    content = json.dumps(
        {
            "name": "demo-app",
            "version": "1.0.0",
            "lockfileVersion": 3,
            "packages": {
                "": {"name": "demo-app", "dependencies": {"express": "^4.18.2"}},
                "node_modules/express": {
                    "version": "4.18.2",
                    "resolved": "https://registry.npmjs.org/express/-/express-4.18.2.tgz",
                    "integrity": "sha512-5/PsL6iVEkiGu9824PNKh45umHMvwZUKR4HC22DJloFHM9ca95QB7p4U29vc83w22K==",
                    "dependencies": {"accepts": "~1.3.8", "qs": "6.11.0"},
                },
                "node_modules/express/node_modules/qs": {"version": "6.11.0"},
                "node_modules/accepts": {"version": "1.3.8"},
            },
        }
    )

    packages, relationships = parser.parse_package_lock(content, "package-lock.json")
    pkg_map = {p.name: p for p in packages}

    assert "express" in pkg_map
    assert pkg_map["express"].version == "4.18.2"
    assert pkg_map["express"].version_confidence == "exact"
    assert pkg_map["express"].integrity is not None

    assert "accepts" in pkg_map
    assert pkg_map["accepts"].version == "1.3.8"
    assert pkg_map["accepts"].dependency_type == "transitive"

    # Relationship from express to accepts
    rel_pairs = [(r.source_name, r.target_name) for r in relationships]
    assert ("express", "accepts") in rel_pairs
    assert ("express", "qs") in rel_pairs


def test_merge_declarations_with_lockfile(parser):
    """Crucial rule: Lockfile exact version wins over declared range."""
    declarations, _ = parser.parse_package_json(json.dumps({"dependencies": {"axios": "^1.7.0"}}), "package.json")
    lock_pkgs, lock_rels = parser.parse_package_lock(
        json.dumps(
            {
                "lockfileVersion": 3,
                "packages": {
                    "node_modules/axios": {
                        "version": "1.7.4",
                        "dependencies": {"follow-redirects": "^1.15.6"},
                    },
                    "node_modules/follow-redirects": {"version": "1.15.6"},
                },
            }
        ),
        "package-lock.json",
    )

    merged, rels = parser.merge_declarations_with_lockfile(declarations, lock_pkgs, lock_rels)
    merged_map = {p.name: p for p in merged}

    assert "axios" in merged_map
    # Resolved exact version from lockfile!
    assert merged_map["axios"].version == "1.7.4"
    assert merged_map["axios"].version_confidence == "exact"
    # Preserved direct dependency type from package.json!
    assert merged_map["axios"].dependency_type == "direct"

    # Transitive package present
    assert "follow-redirects" in merged_map
    assert merged_map["follow-redirects"].dependency_type == "transitive"


def test_invalid_json_handling(parser):
    packages, rels = parser.parse_package_json("{invalid: json", "package.json")
    assert packages == []
    assert rels == []

    packages, rels = parser.parse_package_lock("{invalid: json", "package-lock.json")
    assert packages == []
    assert rels == []
