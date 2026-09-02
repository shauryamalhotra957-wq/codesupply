import pytest
from scanner.sbom.differ import SbomDiffer


def test_sbom_differ_additions_and_removals():
    base_components = [
        {"name": "requests", "version": "2.28.0", "ecosystem": "pypi"},
        {"name": "flask", "version": "2.0.0", "ecosystem": "pypi"},
    ]

    target_components = [
        {"name": "requests", "version": "2.31.0", "ecosystem": "pypi"},  # upgraded
        {"name": "fastapi", "version": "0.100.0", "ecosystem": "pypi"},  # added
        # flask removed
    ]

    diff = SbomDiffer.compare_projects(
        base_project_id="proj_1",
        target_project_id="proj_2",
        base_components=base_components,
        target_components=target_components,
    )

    assert diff["added_count"] == 1
    assert diff["added_components"][0]["name"] == "fastapi"

    assert diff["removed_count"] == 1
    assert diff["removed_components"][0]["name"] == "flask"

    assert diff["version_changes_count"] == 1
    assert diff["version_changes"][0]["name"] == "requests"
    assert diff["version_changes"][0]["old_version"] == "2.28.0"
    assert diff["version_changes"][0]["new_version"] == "2.31.0"
    assert diff["version_changes"][0]["change_type"] == "UPGRADE"


def test_sbom_differ_vulnerability_delta():
    # Base has vulnerable requests 2.28.0
    base_components = [
        {"name": "requests", "version": "2.28.0", "ecosystem": "pypi"},
    ]

    # Target fixes requests to 2.31.0 but introduces vulnerable lodash 4.17.15
    target_components = [
        {"name": "requests", "version": "2.31.0", "ecosystem": "pypi"},
        {"name": "lodash", "version": "4.17.15", "ecosystem": "npm"},
    ]

    diff = SbomDiffer.compare_projects(
        base_project_id="proj_1",
        target_project_id="proj_2",
        base_components=base_components,
        target_components=target_components,
    )

    # requests CVE-2023-32681 resolved
    assert any(v["cve_id"] == "CVE-2023-32681" for v in diff["resolved_vulnerabilities"])

    # lodash CVE-2020-8203 introduced
    assert any(v["cve_id"] == "CVE-2020-8203" for v in diff["new_vulnerabilities"])
