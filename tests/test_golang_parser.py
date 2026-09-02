import tempfile
from pathlib import Path
from scanner.parsers.golang_parser import GolangParser


def test_go_mod_parsing():
    content = """
    module github.com/example/my-go-service

    go 1.21

    require (
        github.com/gin-gonic/gin v1.9.1
        github.com/google/uuid v1.4.0
        golang.org/x/crypto v0.14.0 // indirect
    )
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix="go.mod", delete=False, encoding="utf-8") as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        parser = GolangParser()
        assert parser.can_parse("go.mod") is True
        assert parser.can_parse("go.sum") is True

        deps = parser.parse(tmp_path, "go.mod")
        assert len(deps) == 3

        gin = next(d for d in deps if d.name == "github.com/gin-gonic/gin")
        assert gin.version == "1.9.1"
        assert gin.direct is True
        assert gin.ecosystem == "golang"

        crypto = next(d for d in deps if d.name == "golang.org/x/crypto")
        assert crypto.version == "0.14.0"
        assert crypto.direct is False
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_go_sum_parsing():
    content = """
    github.com/gin-gonic/gin v1.9.1 h1:4+fr/nD8nGWPda/ipElPWOUncq3Nq2w27EFURIECrYo=
    github.com/gin-gonic/gin v1.9.1/go.mod h1:hPrL7YrpYKXt5YId3A/Tnip5kqbEAP+KdLvl9bfhmRI=
    github.com/google/uuid v1.4.0 h1:e0Oxd28EDDmO6g5mtmbhVExoPt16V45rSpP1066pUC4=
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix="go.sum", delete=False, encoding="utf-8") as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        parser = GolangParser()
        deps = parser.parse(tmp_path, "go.sum")
        assert len(deps) == 2
        gin = next(d for d in deps if d.name == "github.com/gin-gonic/gin")
        assert gin.version == "1.9.1"
        assert gin.integrity == "h1:4+fr/nD8nGWPda/ipElPWOUncq3Nq2w27EFURIECrYo="
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
