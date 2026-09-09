"""Dependency relationship construction with evidence tracking."""

import uuid

from app.services.normalizer import ParsedRelationship


class RelationshipBuilder:
    """Builds dependency edge records from parsed relationships."""

    def build_edges(
        self,
        parsed_relationships: list[ParsedRelationship],
        component_map: dict[str, str],  # normalized_name -> component_id
        scan_id: str,
    ) -> tuple[list[dict], list[dict]]:
        """Build dependency edge dicts + evidence dicts.

        Args:
            parsed_relationships: Parsed relationship records from parsers
            component_map: Maps normalized component names to their IDs
            scan_id: The scan these belong to

        Returns:
            (list_of_edge_dicts, list_of_evidence_dicts)
        """
        edges = []
        evidences = []
        seen_edges: set[tuple[str, str]] = set()

        for rel in parsed_relationships:
            source_id = component_map.get(rel.source_name.lower())
            target_id = component_map.get(rel.target_name.lower())

            if not source_id or not target_id:
                continue

            # Deduplicate edges
            edge_key = (source_id, target_id)
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)

            edge_id = uuid.uuid4().hex

            edges.append(
                {
                    "id": edge_id,
                    "source_component_id": source_id,
                    "target_component_id": target_id,
                    "relationship_type": "DEPENDS_ON",
                    "confidence": rel.confidence,
                    "source_file": rel.source_file,
                    "evidence_method": rel.evidence_method,
                }
            )

            evidences.append(
                {
                    "edge_id": edge_id,
                    "source_file": rel.source_file,
                    "source_location": None,
                    "method": rel.evidence_method,
                    "confidence": rel.confidence,
                    "value": f"{rel.source_name} → {rel.target_name}",
                    "evidence_type": "relationship",
                }
            )

        return edges, evidences
