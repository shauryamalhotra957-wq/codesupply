import tempfile
from pathlib import Path
from scanner.parsers.gemfile_parser import GemfileParser
from scanner.parsers.composer_parser import ComposerParser
from scanner.normalization.normalizer import DependencyNormalizer


def test_gemfile_parser():
    parser = GemfileParser()
    assert parser.can_parse("Gemfile")
    assert parser.can_parse("Gemfile.lock")

    lock_content = """
GEM
  remote: https://rubygems.org/
  specs:
    actionmailer (7.1.3.2)
      actionpack (= 7.1.3.2)
      actionview (= 7.1.3.2)
    rails (7.1.3.2)
      actionmailer (= 7.1.3.2)

PLATFORMS
  ruby

DEPENDENCIES
  rails (~> 7.1.3)

BUNDLED WITH
   2.5.6
"""
    with tempfile.NamedTemporaryFile("w+", suffix="Gemfile.lock", delete=False) as f:
        f.write(lock_content)
        f.flush()
        f_path = Path(f.name)

    try:
        deps = parser.parse(f_path, "Gemfile.lock")
        assert len(deps) == 2
        names = {d.name: d for d in deps}
        assert "rails" in names
        assert names["rails"].version == "7.1.3.2"
        assert names["rails"].direct is True
        assert names["rails"].ecosystem == "gem"

        assert "actionmailer" in names
        assert names["actionmailer"].direct is False
        assert "actionpack" in names["actionmailer"].dependencies

        purl = DependencyNormalizer.generate_purl("rails", "7.1.3.2", "gem")
        assert purl == "pkg:gem/rails@7.1.3.2"
    finally:
        f_path.unlink()


def test_composer_parser():
    parser = ComposerParser()
    assert parser.can_parse("composer.json")
    assert parser.can_parse("composer.lock")

    composer_json = """{
        "require": {
            "monolog/monolog": "^2.0",
            "guzzlehttp/guzzle": "^7.0"
        },
        "require-dev": {
            "phpunit/phpunit": "^9.5"
        }
    }"""

    with tempfile.NamedTemporaryFile("w+", suffix="composer.json", delete=False) as f:
        f.write(composer_json)
        f.flush()
        f_path = Path(f.name)

    try:
        deps = parser.parse(f_path, "composer.json")
        assert len(deps) == 3
        names = {d.name: d for d in deps}
        assert "monolog/monolog" in names
        assert names["monolog/monolog"].direct is True
        assert names["monolog/monolog"].scope == "required"
        assert "phpunit/phpunit" in names
        assert names["phpunit/phpunit"].scope == "dev"

        purl = DependencyNormalizer.generate_purl("monolog/monolog", "2.9.1", "composer")
        assert purl == "pkg:composer/monolog/monolog@2.9.1"
    finally:
        f_path.unlink()
