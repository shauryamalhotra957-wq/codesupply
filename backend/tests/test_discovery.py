"""Unit tests for manifest discovery and ecosystem detection."""

from app.scanners.discovery import discover_manifests


def test_discover_manifests(tmp_path):
    # Supported manifests
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "package-lock.json").write_text("{}")
    (tmp_path / "requirements.txt").write_text("flask==3.0.0")
    (tmp_path / "pyproject.toml").write_text("[project]")
    (tmp_path / "pom.xml").write_text("<project></project>")
    (tmp_path / "go.mod").write_text("module demo")
    (tmp_path / "Cargo.toml").write_text("[package]")

    # Detection-only
    (tmp_path / "composer.json").write_text("{}")
    (tmp_path / "App.csproj").write_text("<Project></Project>")
    (tmp_path / "go.sum").write_text("")

    # Ignored directory with dummy manifest that should NOT be discovered
    ignored_nm = tmp_path / "node_modules" / "some-lib"
    ignored_nm.mkdir(parents=True)
    (ignored_nm / "package.json").write_text("{}")

    ignored_git = tmp_path / ".git"
    ignored_git.mkdir(parents=True)
    (ignored_git / "package.json").write_text("{}")

    discovered = discover_manifests(tmp_path)
    disc_paths = [m.path for m in discovered]

    # Check supported manifests
    assert "package.json" in disc_paths
    assert "package-lock.json" in disc_paths
    assert "requirements.txt" in disc_paths
    assert "pyproject.toml" in disc_paths
    assert "pom.xml" in disc_paths
    assert "go.mod" in disc_paths
    assert "Cargo.toml" in disc_paths

    # Check supported status for Go and Cargo
    go_manifest = next((m for m in discovered if m.path == "go.mod"), None)
    assert go_manifest is not None
    assert go_manifest.is_supported is True
    assert go_manifest.ecosystem == "golang"

    rust_manifest = next((m for m in discovered if m.path == "Cargo.toml"), None)
    assert rust_manifest is not None
    assert rust_manifest.is_supported is True
    assert rust_manifest.ecosystem == "cargo"

    # Check detection-only status
    php_manifest = next((m for m in discovered if m.path == "composer.json"), None)
    assert php_manifest is not None
    assert php_manifest.is_supported is False
    assert php_manifest.ecosystem == "php"

    # Ensure node_modules and .git were ignored
    assert not any("node_modules" in p for p in disc_paths)
    assert not any(".git" in p for p in disc_paths)
