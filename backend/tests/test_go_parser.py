"""Tests for Go module parser."""

from app.scanners.go.parser import GoParser


def test_parse_go_mod_basic():
    content = """module github.com/example/my-project

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    golang.org/x/crypto v0.14.0 // indirect
    github.com/stretchr/testify v1.8.4
)
"""
    parser = GoParser()
    pkgs, rels = parser.parse_go_mod(content, "go.mod")

    assert len(pkgs) == 3
    gin = next(p for p in pkgs if p.name == "github.com/gin-gonic/gin")
    assert gin.version == "1.9.1"
    assert gin.dependency_type == "direct"
    assert gin.ecosystem == "golang"
    assert gin.version_confidence == "exact"

    crypto = next(p for p in pkgs if p.name == "golang.org/x/crypto")
    assert crypto.version == "0.14.0"
    assert crypto.dependency_type == "transitive"  # // indirect

    testify = next(p for p in pkgs if p.name == "github.com/stretchr/testify")
    assert testify.dependency_type == "direct"

    # Verify relationships are linked to module name
    assert len(rels) == 3
    for rel in rels:
        assert rel.source_name == "github.com/example/my-project"


def test_parse_go_mod_single_line_require():
    content = """module example.com/app

require rsc.io/quote v1.5.2
"""
    parser = GoParser()
    pkgs, rels = parser.parse_go_mod(content, "go.mod")

    assert len(pkgs) == 1
    assert pkgs[0].name == "rsc.io/quote"
    assert pkgs[0].version == "1.5.2"


def test_parse_go_mod_replace_directive():
    content = """module example.com/app

require (
    golang.org/x/sys v0.0.0-20210616094352-59db8d763f22
)

replace golang.org/x/sys => golang.org/x/sys v0.1.0
"""
    parser = GoParser()
    pkgs, _ = parser.parse_go_mod(content, "go.mod")

    assert len(pkgs) == 1
    assert pkgs[0].name == "golang.org/x/sys"
    assert pkgs[0].version == "0.1.0"


def test_parse_go_mod_empty_or_comments():
    parser = GoParser()
    pkgs, rels = parser.parse_go_mod("// just comments\n\n", "go.mod")
    assert len(pkgs) == 0
    assert len(rels) == 0
