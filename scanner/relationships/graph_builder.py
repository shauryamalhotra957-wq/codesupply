from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple

from scanner.normalization.normalizer import NormalizedComponent


@dataclass
class GraphNode:
    id: str
    label: str
    name: str
    version: str
    ecosystem: str
    direct: bool
    purl: str
    source_file: str
    level: int
    has_findings: bool = False
    findings_count: int = 0

    def to_react_flow(self, x: float = 0, y: float = 0) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": "customDependencyNode",
            "position": {"x": x, "y": y},
            "data": {
                "id": self.id,
                "label": self.label,
                "name": self.name,
                "version": self.version,
                "ecosystem": self.ecosystem,
                "direct": self.direct,
                "purl": self.purl,
                "source_file": self.source_file,
                "level": self.level,
                "has_findings": self.has_findings,
                "findings_count": self.findings_count,
            },
        }


@dataclass
class GraphEdge:
    id: str
    source: str
    target: str
    edge_type: str = "direct"  # direct, transitive

    def to_react_flow(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "type": "smoothstep",
            "animated": self.edge_type == "direct",
            "style": {
                "stroke": "#6366f1" if self.edge_type == "direct" else "#94a3b8",
                "strokeWidth": 1.5,
            },
        }


class DependencyGraphBuilder:
    """
    Constructs the dependency tree and directed acyclic graph (DAG)
    for CycloneDX representation and React Flow visualization.
    """

    @classmethod
    def build_graph(
        cls,
        project_name: str,
        components: List[NormalizedComponent],
        findings_map: Dict[str, int] = None,
    ) -> Dict[str, Any]:
        if findings_map is None:
            findings_map = {}

        root_id = "root:application"
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        # 1. Root Node representing the project itself
        nodes.append(
            GraphNode(
                id=root_id,
                label=project_name,
                name=project_name,
                version="1.0.0",
                ecosystem="app",
                direct=True,
                purl=f"pkg:generic/{project_name}@1.0.0",
                source_file="workspace",
                level=0,
                has_findings=False,
                findings_count=0,
            )
        )

        # Index components by name and PURL
        comp_by_name: Dict[str, NormalizedComponent] = {c.name.lower(): c for c in components}
        comp_by_purl: Dict[str, NormalizedComponent] = {c.purl: c for c in components}

        added_node_ids: Set[str] = {root_id}
        added_edges: Set[Tuple[str, str]] = set()

        # CycloneDX dependency format mapping
        cyclonedx_dependencies: Dict[str, Set[str]] = {f"pkg:generic/{project_name}@1.0.0": set()}

        # 2. Add Direct Components (Level 1)
        direct_components = [c for c in components if c.direct]
        transitive_components = [c for c in components if not c.direct]

        for c in direct_components:
            node_id = c.purl
            if node_id not in added_node_ids:
                f_count = findings_map.get(c.name.lower(), 0)
                nodes.append(
                    GraphNode(
                        id=node_id,
                        label=f"{c.name}@{c.version}" if c.version else c.name,
                        name=c.name,
                        version=c.version or "unpinned",
                        ecosystem=c.ecosystem,
                        direct=True,
                        purl=c.purl,
                        source_file=c.source_file,
                        level=1,
                        has_findings=f_count > 0,
                        findings_count=f_count,
                    )
                )
                added_node_ids.add(node_id)

            # Edge from Root -> Direct Dependency
            edge_key = (root_id, node_id)
            if edge_key not in added_edges:
                edges.append(
                    GraphEdge(
                        id=f"e_{root_id}->{node_id}",
                        source=root_id,
                        target=node_id,
                        edge_type="direct",
                    )
                )
                added_edges.add(edge_key)
                cyclonedx_dependencies[f"pkg:generic/{project_name}@1.0.0"].add(node_id)

        # 3. Add Transitive Components and resolve child links
        for c in components:
            parent_purl = c.purl
            cyclonedx_dependencies.setdefault(parent_purl, set())

            for sub_name in c.dependencies:
                sub_norm = sub_name.lower().strip()
                child_comp = comp_by_name.get(sub_norm)

                if child_comp:
                    child_purl = child_comp.purl
                    # Ensure child node exists
                    if child_purl not in added_node_ids:
                        f_count = findings_map.get(child_comp.name.lower(), 0)
                        nodes.append(
                            GraphNode(
                                id=child_purl,
                                label=f"{child_comp.name}@{child_comp.version}" if child_comp.version else child_comp.name,
                                name=child_comp.name,
                                version=child_comp.version or "unpinned",
                                ecosystem=child_comp.ecosystem,
                                direct=child_comp.direct,
                                purl=child_purl,
                                source_file=child_comp.source_file,
                                level=2,
                                has_findings=f_count > 0,
                                findings_count=f_count,
                            )
                        )
                        added_node_ids.add(child_purl)

                    # Edge from Parent -> Child
                    if (parent_purl, child_purl) not in added_edges and parent_purl != child_purl:
                        edges.append(
                            GraphEdge(
                                id=f"e_{parent_purl}->{child_purl}",
                                source=parent_purl,
                                target=child_purl,
                                edge_type="transitive",
                            )
                        )
                        added_edges.add((parent_purl, child_purl))
                        cyclonedx_dependencies[parent_purl].add(child_purl)

        # Ensure any leftover transitive component is also added as a node
        for c in transitive_components:
            if c.purl not in added_node_ids:
                f_count = findings_map.get(c.name.lower(), 0)
                nodes.append(
                    GraphNode(
                        id=c.purl,
                        label=f"{c.name}@{c.version}" if c.version else c.name,
                        name=c.name,
                        version=c.version or "unpinned",
                        ecosystem=c.ecosystem,
                        direct=False,
                        purl=c.purl,
                        source_file=c.source_file,
                        level=2,
                        has_findings=f_count > 0,
                        findings_count=f_count,
                    )
                )
                added_node_ids.add(c.purl)

        # Format React Flow nodes with hierarchical grid coordinates
        react_flow_nodes = cls._layout_nodes(nodes)
        react_flow_edges = [e.to_react_flow() for e in edges]

        # Convert CycloneDX dependencies to standard list format
        cdx_deps_list = [
            {"ref": ref, "dependsOn": sorted(list(deps))}
            for ref, deps in cyclonedx_dependencies.items()
            if deps or ref == f"pkg:generic/{project_name}@1.0.0"
        ]

        return {
            "root_id": root_id,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "react_flow": {
                "nodes": react_flow_nodes,
                "edges": react_flow_edges,
            },
            "cyclonedx_dependencies": cdx_deps_list,
        }

    @staticmethod
    def _layout_nodes(nodes: List[GraphNode]) -> List[Dict[str, Any]]:
        """Calculates tidy hierarchical positions for nodes based on level."""
        level_groups: Dict[int, List[GraphNode]] = {}
        for n in nodes:
            level_groups.setdefault(n.level, []).append(n)

        laid_out = []
        x_spacing = 280
        y_spacing = 110

        for level, group in level_groups.items():
            total_in_level = len(group)
            x_start = level * x_spacing
            y_offset = -((total_in_level - 1) * y_spacing) / 2.0

            for idx, node in enumerate(group):
                y_pos = y_offset + (idx * y_spacing)
                laid_out.append(node.to_react_flow(x=x_start, y=y_pos))

        return laid_out
