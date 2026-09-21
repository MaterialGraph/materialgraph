from sqlalchemy.orm import Session

from app.services.material.neighbor_service import (
    MaterialNeighborService,
    neighbor_ranking_key,
)


class MaterialNeighborhoodService:
    def __init__(self, db: Session):
        self.db = db
        self.neighbor_service = MaterialNeighborService(db)

    def get_neighborhood(
        self,
        material_id: int,
        depth: int = 2,
        limit: int = 25,
    ) -> dict:
        neighbor_cache: dict[int, dict] = {}

        root = self._get_neighbors_batch(
            material_ids=[material_id],
            cache=neighbor_cache,
        )[material_id]

        if root["mp_id"] is None:
            return self._empty_neighborhood_response(
                material_id=material_id,
                depth=depth,
            )

        visited: set[int] = {material_id}
        frontier: list[int] = [material_id]

        nodes: dict[int, dict] = {
            material_id: {
                "material_id": root["material_id"],
                "mp_id": root["mp_id"],
                "pretty_formula": root["pretty_formula"],
                "formula": root["formula"],
                "material_type": root["material_type"],
                "is_stable": root["is_stable"],
                "energy_above_hull": root["energy_above_hull"],
                "depth": 0,
                "best_score": 0,
            }
        }

        edges: list[dict] = []

        current_depth = 0
        while frontier and current_depth < depth:
            neighbors_by_material = self._get_neighbors_batch(
                material_ids=frontier,
                cache=neighbor_cache,
            )
            next_frontier: list[int] = []

            for current_id in frontier:
                current_neighbors = neighbors_by_material[current_id]

                ordered_neighbors = sorted(
                    current_neighbors["neighbors"],
                    key=neighbor_ranking_key,
                )

                for neighbor in ordered_neighbors:
                    neighbor_id = neighbor["material_id"]
                    next_depth = current_depth + 1

                    if neighbor_id not in nodes:
                        if len(nodes) >= limit:
                            continue

                        nodes[neighbor_id] = {
                            "material_id": neighbor_id,
                            "mp_id": neighbor["mp_id"],
                            "pretty_formula": neighbor["pretty_formula"],
                            "formula": neighbor["formula"],
                            "material_type": neighbor["material_type"],
                            "is_stable": neighbor["is_stable"],
                            "energy_above_hull": neighbor["energy_above_hull"],
                            "depth": next_depth,
                            "best_score": neighbor["neighbor_score"],
                        }

                    else:
                        nodes[neighbor_id]["best_score"] = max(
                            nodes[neighbor_id]["best_score"],
                            neighbor["neighbor_score"],
                        )

                    edges.append(
                        {
                            "source_material_id": current_id,
                            "target_material_id": neighbor_id,
                            "relationship_types": neighbor["relationship_types"],
                            "shared_element_count": neighbor[
                                "shared_element_count"
                            ],
                            "shared_application_count": neighbor[
                                "shared_application_count"
                            ],
                            "edge_score": neighbor["neighbor_score"],
                        }
                    )

                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        next_frontier.append(neighbor_id)

            frontier = next_frontier
            current_depth += 1

        sorted_nodes = sorted(
            nodes.values(),
            key=lambda item: (item["depth"], -item["best_score"], item["material_id"]),
        )

        sorted_edges = sorted(
            edges,
            key=lambda item: (
                -item["edge_score"],
                item["source_material_id"],
                item["target_material_id"],
            ),
        )

        limited_nodes = sorted_nodes[:limit]
        limited_node_ids = {
            node["material_id"]
            for node in limited_nodes
        }

        limited_edges = [
            edge
            for edge in sorted_edges
            if edge["source_material_id"] in limited_node_ids
            and edge["target_material_id"] in limited_node_ids
        ][:limit]

        return {
            "material_id": root["material_id"],
            "mp_id": root["mp_id"],
            "pretty_formula": root["pretty_formula"],
            "formula": root["formula"],
            "depth": depth,
            "node_count": len(limited_nodes),
            "edge_count": len(limited_edges),
            "nodes": limited_nodes,
            "edges": limited_edges,
        }

    def _get_neighbors_batch(
        self,
        material_ids: list[int],
        cache: dict[int, dict],
    ) -> dict[int, dict]:
        missing_material_ids = [
            material_id
            for material_id in material_ids
            if material_id not in cache
        ]
        if missing_material_ids:
            cache.update(
                self.neighbor_service.get_neighbors_batch(missing_material_ids)
            )

        return {
            material_id: cache[material_id]
            for material_id in material_ids
        }

    def _empty_neighborhood_response(
        self,
        material_id: int,
        depth: int,
    ) -> dict:
        return {
            "material_id": material_id,
            "mp_id": None,
            "pretty_formula": None,
            "formula": None,
            "depth": depth,
            "node_count": 0,
            "edge_count": 0,
            "nodes": [],
            "edges": [],
        }
