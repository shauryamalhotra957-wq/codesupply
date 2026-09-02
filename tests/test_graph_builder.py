from scanner.normalization.normalizer import NormalizedComponent
from scanner.relationships.graph_builder import DependencyGraphBuilder


def test_dependency_graph_builder():
    components = [
        NormalizedComponent(
            name="fastapi",
            version="0.110.0",
            ecosystem="pypi",
            direct=True,
            purl="pkg:pypi/fastapi@0.110.0",
            source_file="requirements.txt",
            dependencies=["starlette", "pydantic"],
        ),
        NormalizedComponent(
            name="starlette",
            version="0.36.3",
            ecosystem="pypi",
            direct=False,
            purl="pkg:pypi/starlette@0.36.3",
            source_file="requirements.txt",
            dependencies=["anyio"],
        ),
        NormalizedComponent(
            name="pydantic",
            version="2.6.4",
            ecosystem="pypi",
            direct=False,
            purl="pkg:pypi/pydantic@2.6.4",
            source_file="requirements.txt",
        ),
        NormalizedComponent(
            name="anyio",
            version="4.3.0",
            ecosystem="pypi",
            direct=False,
            purl="pkg:pypi/anyio@4.3.0",
            source_file="requirements.txt",
        ),
    ]

    graph = DependencyGraphBuilder.build_graph(
        project_name="my-app",
        components=components,
        findings_map={"fastapi": 1},
    )

    assert graph["total_nodes"] == 5  # root + 4 components
    assert graph["root_id"] == "root:application"

    rf_nodes = graph["react_flow"]["nodes"]
    rf_edges = graph["react_flow"]["edges"]

    # Check root node
    root_node = next(n for n in rf_nodes if n["id"] == "root:application")
    assert root_node["data"]["label"] == "my-app"

    # Check finding indicator
    fastapi_node = next(n for n in rf_nodes if n["data"]["name"] == "fastapi")
    assert fastapi_node["data"]["has_findings"] is True
    assert fastapi_node["data"]["findings_count"] == 1

    # Check edges exist
    edge_sources = [e["source"] for e in rf_edges]
    edge_targets = [e["target"] for e in rf_edges]

    assert "root:application" in edge_sources
    assert "pkg:pypi/fastapi@0.110.0" in edge_targets
    assert "pkg:pypi/fastapi@0.110.0" in edge_sources
    assert "pkg:pypi/starlette@0.36.3" in edge_targets
