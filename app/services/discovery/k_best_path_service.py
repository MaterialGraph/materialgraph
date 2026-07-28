from collections import deque

from sqlalchemy.orm import Session

from app.services.discovery.graph_builder import DiscoveryGraphBuilder
from app.services.discovery.path_ranking_service import DiscoveryPathRankingService


class DiscoveryKBestPathService:
    DEFAULT_MAX_HOPS = 2
    DEFAULT_K = 5
    INTERNAL_PATH_LIMIT = 100
    INTERNAL_STATE_LIMIT = 1000

    def __init__(self, db: Session):
        self.db = db
        self.graph_builder = DiscoveryGraphBuilder(db)
        self.path_ranking_service = DiscoveryPathRankingService(db)

    def get_k_best_paths(
        self,
        start_material_id: int,
        target_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_hops: int = DEFAULT_MAX_HOPS,
        k: int = DEFAULT_K,
    ) -> dict:
        ranked_paths, search_truncated = self._build_ranked_paths(
            start_material_id=start_material_id,
            target_material_id=target_material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_hops=max_hops,
        )

        ranked_paths.sort(
            key=lambda item: item["scientific_usefulness_score"],
            reverse=True,
        )

        limited_paths = ranked_paths[:k]

        return {
            "algorithm": "k_best_paths",
            "start_material_id": start_material_id,
            "target_material_id": target_material_id,
            "path_count": len(limited_paths),
            "total_path_count": len(ranked_paths),
            "search_truncated": search_truncated,
            "k": k,
            "max_hops": max_hops,
            "paths": limited_paths,
        }

    def get_k_shortest_paths(
        self,
        start_material_id: int,
        target_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_hops: int = DEFAULT_MAX_HOPS,
        k: int = DEFAULT_K,
    ) -> dict:
        ranked_paths, search_truncated = self._build_ranked_paths(
            start_material_id=start_material_id,
            target_material_id=target_material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_hops=max_hops,
        )

        ranked_paths.sort(
            key=lambda item: (
                item["hop_count"],
                -item["scientific_usefulness_score"],
            ),
        )

        limited_paths = ranked_paths[:k]

        return {
            "algorithm": "k_shortest_paths",
            "start_material_id": start_material_id,
            "target_material_id": target_material_id,
            "path_count": len(limited_paths),
            "total_path_count": len(ranked_paths),
            "search_truncated": search_truncated,
            "k": k,
            "max_hops": max_hops,
            "paths": limited_paths,
        }

    def _build_ranked_paths(
        self,
        start_material_id: int,
        target_material_id: int,
        avoid_element: str | None,
        prefer_element: str | None,
        max_hops: int,
    ) -> tuple[list[dict], bool]:
        adjacency = self.graph_builder.build_adjacency(
            start_material_id=start_material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_depth=max_hops,
        )

        paths, search_truncated = self._enumerate_simple_paths(
            start_material_id=start_material_id,
            target_material_id=target_material_id,
            adjacency=adjacency,
            max_hops=max_hops,
        )

        ranked_paths = []

        for path_ids in paths:
            materials = self._materials_for_path(
                path_ids=path_ids,
                adjacency=adjacency,
                start_material_id=start_material_id,
            )

            transitions = self._transitions_for_path(
                path_ids=path_ids,
                adjacency=adjacency,
            )

            ranking = self.path_ranking_service.rank_path(
                materials=materials,
                transitions=transitions,
                avoid_element=avoid_element,
                prefer_element=prefer_element,
            )

            ranked_paths.append(
                {
                    "hop_count": len(transitions),
                    "material_ids": path_ids,
                    "materials": materials,
                    "transitions": transitions,
                    **ranking,
                }
            )

        return ranked_paths, search_truncated

    def _enumerate_simple_paths(
        self,
        start_material_id: int,
        target_material_id: int,
        adjacency: dict[int, list[dict]],
        max_hops: int,
    ) -> tuple[list[list[int]], bool]:
        paths: list[list[int]] = []
        queue = deque([(start_material_id, [start_material_id])])
        processed_states = 0
        search_truncated = False

        while queue:
            if processed_states >= self.INTERNAL_STATE_LIMIT:
                search_truncated = True
                break

            current_id, path = queue.popleft()
            processed_states += 1
            hop_count = len(path) - 1

            if hop_count > max_hops:
                continue

            if current_id == target_material_id:
                paths.append(path)

                if len(paths) >= self.INTERNAL_PATH_LIMIT:
                    search_truncated = bool(queue)
                    break

                continue

            if hop_count == max_hops:
                continue

            for candidate in adjacency.get(current_id, []):
                next_id = candidate["material_id"]

                if next_id in path:
                    continue

                queue.append((next_id, [*path, next_id]))

        return paths, search_truncated

    def _materials_for_path(
        self,
        path_ids: list[int],
        adjacency: dict[int, list[dict]],
        start_material_id: int,
    ) -> list[dict]:
        materials = []

        for index, material_id in enumerate(path_ids):
            if index == 0:
                materials.append({"material_id": start_material_id})
                continue

            candidate = self._find_candidate_in_adjacency(
                source_id=path_ids[index - 1],
                target_id=material_id,
                adjacency=adjacency,
            )

            if candidate is None:
                materials.append({"material_id": material_id})
                continue

            materials.append(
                {
                    "material_id": candidate["material_id"],
                    "mp_id": candidate.get("mp_id"),
                    "pretty_formula": candidate.get("pretty_formula"),
                    "formula": candidate.get("pretty_formula")
                    or candidate.get("formula"),
                    "discovery_score": candidate.get("discovery_score"),
                    "discovery_path": candidate.get("discovery_path", []),
                    "explanation": candidate.get("explanation"),
                }
            )

        return materials

    def _transitions_for_path(
        self,
        path_ids: list[int],
        adjacency: dict[int, list[dict]],
    ) -> list[dict]:
        transitions = []

        for source_id, target_id in zip(path_ids, path_ids[1:]):
            candidate = self._find_candidate_in_adjacency(
                source_id=source_id,
                target_id=target_id,
                adjacency=adjacency,
            )

            if candidate is None:
                continue

            transition = candidate.get("validated_transition")

            if transition is None:
                continue

            transitions.append(
                {
                    "source_material_id": source_id,
                    "target_material_id": target_id,
                    "transition_type": transition["transition_type"],
                    "family": transition.get("family"),
                    "preserved_framework": transition.get(
                        "preserved_framework",
                        [],
                    ),
                    "preservation_basis": transition.get(
                        "preservation_basis",
                    ),
                    "structural_preservation_validated": transition.get(
                        "structural_preservation_validated",
                        False,
                    ),
                    "removed_elements": transition.get(
                        "removed_elements",
                        [],
                    ),
                    "introduced_elements": transition.get(
                        "introduced_elements",
                        [],
                    ),
                    "scientific_reason": (
                        transition.get("scientific_reason")
                        or transition.get("reason")
                        or "Scientific transition identified by deterministic path rules."
                    ),
                }
            )

        return transitions

    def _find_candidate_in_adjacency(
        self,
        source_id: int,
        target_id: int,
        adjacency: dict[int, list[dict]],
    ) -> dict | None:
        for candidate in adjacency.get(source_id, []):
            if candidate["material_id"] == target_id:
                return candidate

        return None