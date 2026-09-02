import tempfile
from pathlib import Path
from scanner.parsers.cargo_parser import CargoParser


def test_cargo_toml_parsing():
    content = """
    [package]
    name = "my-rust-app"
    version = "0.1.0"
    edition = "2021"

    [dependencies]
    serde = "1.0.197"
    tokio = { version = "1.36.0", features = ["full"] }

    [dev-dependencies]
    criterion = "0.5.1"
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix="Cargo.toml", delete=False, encoding="utf-8") as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        parser = CargoParser()
        assert parser.can_parse("Cargo.toml") is True
        assert parser.can_parse("Cargo.lock") is True

        deps = parser.parse(tmp_path, "Cargo.toml")
        assert len(deps) == 3

        names = {d.name: d for d in deps}
        assert "serde" in names
        assert names["serde"].ecosystem == "cargo"
        assert names["serde"].scope == "required"
        assert names["serde"].version == "1.0.197"

        assert "tokio" in names
        assert names["tokio"].version == "1.36.0"

        assert "criterion" in names
        assert names["criterion"].scope == "dev"
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_cargo_lock_parsing():
    content = """
    version = 3

    [[package]]
    name = "aho-corasick"
    version = "1.1.2"
    source = "registry+https://github.com/rust-lang/crates.io-index"
    checksum = "b2969dcb958b36655471fc61f7e416fa76033bdd4bfed0678d8fee1e2d07a1f0"
    dependencies = [
     "memchr",
    ]

    [[package]]
    name = "memchr"
    version = "2.7.1"
    source = "registry+https://github.com/rust-lang/crates.io-index"
    checksum = "523dc4f511e55ab87b694dc30d0f820d60906ef06413f93d4d7a1385599cc149"
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix="Cargo.lock", delete=False, encoding="utf-8") as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        parser = CargoParser()
        deps = parser.parse(tmp_path, "Cargo.lock")
        assert len(deps) == 2

        aho = next(d for d in deps if d.name == "aho-corasick")
        assert aho.version == "1.1.2"
        assert "memchr" in aho.dependencies
        assert aho.integrity == "sha256:b2969dcb958b36655471fc61f7e416fa76033bdd4bfed0678d8fee1e2d07a1f0"
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
