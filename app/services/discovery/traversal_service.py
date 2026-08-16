from collections import deque

from sqlalchemy.orm import Session

from app.models.material import Material
from app.services.discovery.graph_builder import DiscoveryGraphBuilder
from app.services.discovery.path_ranking_service import DiscoveryPathRankingService


class DiscoveryTraversalService:
    DEFAULT_MAX_HOPS = 2
    MAX_ALLOWED_HOPS = 3
    DEFAULT_LIMIT = 50

    def __init__(self, db: Session):
        self.db = db
        self.graph_builder = DiscoveryGraphBuilder(db)
        self.path_ranking_service = DiscoveryPathRankingService(db)

    def get_graph(
        self,
        material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_hops: int = DEFAULT_MAX_HOPS,
        limit: int = DEFAULT_LIMIT,
    ) -> dict:
        result = self._build_graph_response(
            material_id=material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_hops=max_hops,
            limit=limit,
        )

        limited_nodes, limited_edges = self._limit_graph(
            nodes=result["nodes"],
            edges=result["edges"],
            limit=limit,
        )

        result["nodes"] = limited_nodes
        result["edges"] = limited_edges

        return result


    def _build_graph_response(
        self,
        material_id: int,
        avoid_element: str | None,
        prefer_element: str | None,
        max_hops: int,
        limit: int,
    ) -> dict:
        effective_max_hops = (
            self.graph_builder.get_effective_max_depth(max_hops)
        )

        base_material = self.db.get(Material, material_id)

        if base_material is None:
            return self._empty_response(
                material_id=material_id,
                avoid_element=avoid_element,
                prefer_element=prefer_element,
                max_hops=max_hops,
                effective_max_hops=effective_max_hops,
                limit=limit,
            )

        graph = self.graph_builder.build_graph(
            start_material_id=material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_depth=effective_max_hops,
        )

        return {
            "material_id": base_material.id,
            "mp_id": base_material.mp_id,
            "base_formula": (
                base_material.pretty_formula
                or base_material.formula
            ),
            "graph_goal": {
                "avoid_element": avoid_element,
                "prefer_element": prefer_element,
                "max_hops": max_hops,
                "effective_max_hops": effective_max_hops,
                "limit": limit,
            },
            "nodes": graph["nodes"],
            "edges": graph["edges"],
        }


    def get_subgraph(
        self,
        material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        family: str | None = None,
        transition_type: str | None = None,
        min_quality_score: float | None = None,
        min_edge_score: float | None = None,
        max_hops: int = DEFAULT_MAX_HOPS,
        limit: int = DEFAULT_LIMIT,
    ) -> dict:
        result = self._build_graph_response(
            material_id=material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_hops=max_hops,
            limit=limit,
        )

        edges = self._filter_edges(
            edges=result["edges"],
            family=family,
            transition_type=transition_type,
            min_edge_score=min_edge_score,
        )

        connected_ids = self._collect_connected_node_ids(edges)

        nodes = self._filter_nodes(
            nodes=result["nodes"],
            connected_ids=connected_ids,
            min_quality_score=min_quality_score,
        )

        allowed_node_ids = {
            node["material_id"]
            for node in nodes
        }

        edges = [
            edge for edge in edges
            if (
                edge["source_material_id"] in allowed_node_ids
                and edge["target_material_id"] in allowed_node_ids
            )
        ]

        nodes, edges = self._limit_graph(
            nodes=nodes,
            edges=edges,
            limit=limit,
        )

        result["subgraph_filter"] = {
            "family": family,
            "transition_type": transition_type,
            "prefer_element": prefer_element,
            "avoid_element": avoid_element,
            "min_quality_score": min_quality_score,
            "min_edge_score": min_edge_score,
        }

        result["subgraph_metadata"] = self._build_subgraph_metadata(
            nodes=nodes,
            edges=edges,
        )

        result["nodes"] = nodes
        result["edges"] = edges

        return result

    def _filter_edges(
        self,
        edges: list[dict],
        *,
        family: str | None = None,
        transition_type: str | None = None,
        min_edge_score: float | None = None,
    ) -> list[dict]:
        filtered_edges = edges

        if family:
            filtered_edges = [
                edge for edge in filtered_edges
                if edge.get("family") == family
            ]

        if transition_type:
            filtered_edges = [
                edge for edge in filtered_edges
                if edge.get("transition_type") == transition_type
            ]

        if min_edge_score is not None:
            filtered_edges = [
                edge for edge in filtered_edges
                if (edge.get("edge_score") or 0.0) >= min_edge_score
            ]

        return filtered_edges

    def _collect_connected_node_ids(
        self,
        edges: list[dict],
    ) -> set[int]:
        connected_ids: set[int] = set()

        for edge in edges:
            connected_ids.add(edge["source_material_id"])
            connected_ids.add(edge["target_material_id"])

        return connected_ids

    def _filter_nodes(
        self,
        nodes: list[dict],
        connected_ids: set[int],
        *,
        min_quality_score: float | None = None,
    ) -> list[dict]:
        filtered_nodes = [
            node for node in nodes
            if node["material_id"] in connected_ids
        ]

        if min_quality_score is not None:
            filtered_nodes = [
                node for node in filtered_nodes
                if (node.get("quality_score") or 0.0) >= min_quality_score
            ]

        return filtered_nodes

    def _build_subgraph_metadata(
        self,
        nodes: list[dict],
        edges: list[dict],
    ) -> dict:
        quality_scores = [
            node.get("quality_score") or 0.0
            for node in nodes
        ]

        edge_scores = [
            edge.get("edge_score") or 0.0
            for edge in edges
        ]

        average_quality_score = (
            sum(quality_scores) / len(quality_scores)
            if quality_scores
            else 0.0
        )

        average_edge_score = (
            sum(edge_scores) / len(edge_scores)
            if edge_scores
            else 0.0
        )

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "average_quality_score": round(average_quality_score, 2),
            "average_edge_score": round(average_edge_score, 2),
        }

    def get_path(
        self,
        material_id: int,
        target_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_hops: int = DEFAULT_MAX_HOPS,
    ) -> dict:
        base_material = self.db.get(Material, material_id)

        if base_material is None:
            return self._empty_path_response(material_id, target_material_id)

        graph = self.graph_builder.build_graph(
            start_material_id=material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_depth=max_hops,
        )

        node_by_id = {
            node["material_id"]: node
            for node in graph["nodes"]
        }
        edge_adjacency = self._build_edge_adjacency(graph["edges"])
        path = self._find_shortest_path(
            start_material_id=material_id,
            target_material_id=target_material_id,
            edge_adjacency=edge_adjacency,
            max_hops=max_hops,
        )

        if path is not None:
            path_ids, transitions = path

            if not all(path_id in node_by_id for path_id in path_ids):
                return self._empty_path_response(
                    material_id,
                    target_material_id,
                )

            materials = [
                node_by_id[path_id]
                for path_id in path_ids
            ]
            ranking = self.path_ranking_service.rank_path(
                materials=materials,
                transitions=transitions,
                avoid_element=avoid_element,
                prefer_element=prefer_element,
            )

            return {
                "material_id": material_id,
                "target_material_id": target_material_id,
                "path_found": True,
                "hop_count": len(transitions),
                "materials": materials,
                "transitions": transitions,
                "path_reason": self._build_path_reason(transitions),
                **ranking,
            }

        return self._empty_path_response(material_id, target_material_id)

    def _build_edge_adjacency(
        self,
        edges: list[dict],
    ) -> dict[int, list[dict]]:
        adjacency: dict[int, list[dict]] = {}

        for edge in edges:
            source_id = edge["source_material_id"]
            adjacency.setdefault(source_id, []).append(edge)

        return adjacency

    def _find_shortest_path(
        self,
        start_material_id: int,
        target_material_id: int,
        edge_adjacency: dict[int, list[dict]],
        max_hops: int,
    ) -> tuple[list[int], list[dict]] | None:
        queue = deque(
            [(start_material_id, [start_material_id], [])]
        )

        while queue:
            material_id, path_ids, transitions = queue.popleft()

            if material_id == target_material_id:
                return path_ids, transitions

            if len(transitions) >= max_hops:
                continue

            for edge in edge_adjacency.get(material_id, []):
                next_id = edge["target_material_id"]

                if next_id in path_ids:
                    continue

                queue.append(
                    (
                        next_id,
                        [*path_ids, next_id],
                        [*transitions, edge],
                    )
                )

        return None

    def _build_path_reason(self, transitions: list[dict]) -> str:
        if not transitions:
            return "No discovery path was generated."

        transition_types = [
            transition["transition_type"]
            for transition in transitions
        ]

        shared_element_sets = [
            set(
                transition.get("shared_elements")
                or transition.get("preserved_framework", [])
            )
            for transition in transitions
            if (
                transition.get("shared_elements")
                or transition.get("preserved_framework")
            )
        ]

        common_shared_elements = sorted(
            set.intersection(*shared_element_sets)
            if shared_element_sets
            else set()
        )

        reason = (
            "This discovery path follows "
            + " -> ".join(transition_types)
        )

        if common_shared_elements:
            reason += (
                " while retaining shared elemental overlap across "
                + "-".join(common_shared_elements)
                + "; structural preservation is not validated"
            )

        return reason + "."

    def _empty_response(
        self,
        material_id: int,
        avoid_element: str | None,
        prefer_element: str | None,
        max_hops: int,
        effective_max_hops: int,
        limit: int,
    ) -> dict:
        return {
            "material_id": material_id,
            "mp_id": None,
            "base_formula": None,
            "graph_goal": {
                "avoid_element": avoid_element,
                "prefer_element": prefer_element,
                "max_hops": max_hops,
                "effective_max_hops": effective_max_hops,
                "limit": limit,
            },
            "nodes": [],
            "edges": [],
        }

    def _chain_transition_to_graph_edge(self, transition: dict) -> dict:
        return {
            "source_material_id": transition["from_material_id"],
            "target_material_id": transition["to_material_id"],
            "transition_type": transition["transition_type"],
            "family": transition.get("family"),
            "preserved_framework": transition.get("preserved_framework", []),
            "removed_elements": transition.get("removed_elements", []),
            "introduced_elements": transition.get("introduced_elements", []),
            "scientific_reason": transition.get("reason")
            or "Scientific transition identified by deterministic chain rules.",
        }

    def _material_to_node(self, material: Material) -> dict:
        return {
            "material_id": material.id,
            "mp_id": material.mp_id,
            "pretty_formula": material.pretty_formula,
            "formula": material.pretty_formula or material.formula,
        }


    def _empty_path_response(
        self,
        material_id: int,
        target_material_id: int,
    ) -> dict:
        return {
            "material_id": material_id,
            "target_material_id": target_material_id,
            "path_found": False,
            "hop_count": None,
            "materials": [],
            "transitions": [],
            "path_reason": None,
            "scientific_usefulness_score": None,
            "score_breakdown": None,
            "usefulness_reason": None,
        }


    def _limit_graph(
        self,
        nodes: list[dict],
        edges: list[dict],
        limit: int,
    ) -> tuple[list[dict], list[dict]]:
        limited_nodes = nodes[:limit]

        limited_node_ids = {
            node["material_id"]
            for node in limited_nodes
        }

        limited_edges = [
            edge
            for edge in edges
            if (
                edge["source_material_id"] in limited_node_ids
                and edge["target_material_id"] in limited_node_ids
            )
        ][:limit]

        return limited_nodes, limited_edges