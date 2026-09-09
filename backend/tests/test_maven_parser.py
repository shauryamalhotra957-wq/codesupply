"""Unit tests for Maven pom.xml parser."""

import pytest

from app.scanners.maven.parser import MavenParser


@pytest.fixture
def parser():
    return MavenParser()


def test_parse_pom_xml_with_properties(parser):
    content = """<?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0">
        <modelVersion>4.0.0</modelVersion>
        <groupId>com.example</groupId>
        <artifactId>demo-app</artifactId>
        <version>1.0.0</version>

        <properties>
            <spring.version>6.1.0</spring.version>
            <jackson.version>2.16.1</jackson.version>
        </properties>

        <dependencies>
            <dependency>
                <groupId>org.springframework</groupId>
                <artifactId>spring-core</artifactId>
                <version>${spring.version}</version>
                <scope>compile</scope>
            </dependency>
            <dependency>
                <groupId>com.fasterxml.jackson.core</groupId>
                <artifactId>jackson-databind</artifactId>
                <version>${jackson.version}</version>
            </dependency>
            <dependency>
                <groupId>junit</groupId>
                <artifactId>junit</artifactId>
                <version>4.13.2</version>
                <scope>test</scope>
            </dependency>
        </dependencies>
    </project>
    """

    packages = parser.parse_pom_xml(content, "pom.xml")
    pkg_map = {p.name: p for p in packages}

    # Resolved property reference
    assert "org.springframework:spring-core" in pkg_map
    spring_pkg = pkg_map["org.springframework:spring-core"]
    assert spring_pkg.version == "6.1.0"
    assert spring_pkg.version_confidence == "exact"
    assert spring_pkg.dependency_type == "direct"
    assert spring_pkg.ecosystem == "maven"

    # Default scope is compile -> direct
    assert "com.fasterxml.jackson.core:jackson-databind" in pkg_map
    assert pkg_map["com.fasterxml.jackson.core:jackson-databind"].dependency_type == "direct"

    # Test scope -> dev
    assert "junit:junit" in pkg_map
    assert pkg_map["junit:junit"].dependency_type == "dev"


def test_parse_pom_xml_version_range(parser):
    content = """<project>
        <dependencies>
            <dependency>
                <groupId>org.slf4j</groupId>
                <artifactId>slf4j-api</artifactId>
                <version>[1.7, 1.8)</version>
            </dependency>
        </dependencies>
    </project>"""

    packages = parser.parse_pom_xml(content, "pom.xml")
    assert len(packages) == 1
    assert packages[0].version_confidence == "declared_range"


def test_parse_malformed_pom_xml(parser):
    packages = parser.parse_pom_xml("<not valid xml", "pom.xml")
    assert packages == []
