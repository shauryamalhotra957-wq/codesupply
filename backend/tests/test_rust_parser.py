"""Tests for Rust Cargo.toml parser."""

from app.scanners.rust.parser import RustParser


def test_parse_cargo_toml_basic():
    content = """[package]
name = "my-crate"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0.197", features = ["derive"] }
tokio = "1.36.0"
opt_dep = { version = "0.2.0", optional = true }

[dev-dependencies]
criterion = "0.5.1"
"""
    parser = RustParser()
    pkgs = parser.parse_cargo_toml(content, "Cargo.toml")

    assert len(pkgs) == 4

    serde = next(p for p in pkgs if p.name == "serde")
    assert serde.version == "1.0.197"
    assert serde.dependency_type == "direct"
    assert serde.ecosystem == "cargo"

    tokio = next(p for p in pkgs if p.name == "tokio")
    assert tokio.version == "1.36.0"
    assert tokio.dependency_type == "direct"

    opt = next(p for p in pkgs if p.name == "opt_dep")
    assert opt.dependency_type == "optional"

    criterion = next(p for p in pkgs if p.name == "criterion")
    assert criterion.dependency_type == "dev"


def test_parse_cargo_toml_version_ranges():
    content = """[dependencies]
exact_crate = "=1.2.3"
caret_crate = "^1.2.3"
tilde_crate = "~1.2.3"
range_crate = ">=1.0, <2.0"
"""
    parser = RustParser()
    pkgs = parser.parse_cargo_toml(content, "Cargo.toml")

    exact = next(p for p in pkgs if p.name == "exact_crate")
    assert exact.version == "1.2.3"
    assert exact.version_confidence == "exact"

    caret = next(p for p in pkgs if p.name == "caret_crate")
    assert caret.version_confidence == "declared_range"


def test_parse_cargo_toml_special_dependencies():
    content = """[dependencies]
workspace_crate = { workspace = true }
git_crate = { git = "https://github.com/example/repo" }
"""
    parser = RustParser()
    pkgs = parser.parse_cargo_toml(content, "Cargo.toml")

    assert len(pkgs) == 2
    for pkg in pkgs:
        assert pkg.version_confidence == "unknown"


def test_parse_cargo_toml_malformed():
    parser = RustParser()
    pkgs = parser.parse_cargo_toml("not valid = [toml", "Cargo.toml")
    assert len(pkgs) == 0
