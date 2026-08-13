from sqlalchemy.orm import Session

from app.services.material.criticality_service import MaterialCriticalityService
from app.services.material.neighbor_service import MaterialNeighborService


class MaterialSimilarityService:
    def __init__(self, db: Session):
        self.db = db
        self.neighbor_service = MaterialNeighborService(db)
        self.criticality_service = MaterialCriticalityService(db)

    def get_similar_materials(self, material_id: int, limit: int = 10) -> dict:
        neighbor_result = self.neighbor_service.get_neighbors(material_id)

        if neighbor_result["mp_id"] is None:
            return self._empty_similarity_response(material_id)

        limited_neighbors = neighbor_result["neighbors"][:limit]

        criticality_by_material_id = (
            self.criticality_service.get_material_criticality_bulk(
                material_ids=[
                    material_id,
                    *[
                        neighbor["material_id"]
                        for neighbor in limited_neighbors
                    ],
                ]
            )
        )

        source_criticality_score = criticality_by_material_id[
            material_id
        ]["criticality_score"]

        similar_materials = []

        for neighbor in limited_neighbors:
            neighbor_material_id = neighbor["material_id"]

            similarity_score = self._calculate_similarity_score(neighbor)

            neighbor_criticality_score = criticality_by_material_id[
                neighbor_material_id
            ]["criticality_score"]

            criticality_delta = self._calculate_criticality_delta(
                source_criticality_score=source_criticality_score,
                neighbor_criticality_score=neighbor_criticality_score,
            )

            similar_materials.append(
                {
                    "material_id": neighbor_material_id,
                    "mp_id": neighbor["mp_id"],
                    "pretty_formula": neighbor["pretty_formula"],
                    "formula": neighbor["formula"],
                    "material_type": neighbor["material_type"],
                    "is_stable": neighbor["is_stable"],
                    "energy_above_hull": neighbor["energy_above_hull"],
                    "shared_element_count": neighbor["shared_element_count"],
                    "shared_application_count": neighbor["shared_application_count"],
                    "relationship_types": neighbor["relationship_types"],
                    "similarity_score": similarity_score,
                    "criticality_score": neighbor_criticality_score,
                    "criticality_delta": criticality_delta,
                    "criticality_direction": self._criticality_direction(
                        criticality_delta
                    ),
                    "reason_summary": self._build_reason_summary(
                        neighbor=neighbor,
                        criticality_delta=criticality_delta,
                    ),
                }
            )

        similar_materials.sort(
            key=self._similarity_ranking_key,
            reverse=True,
        )

        return {
            "material_id": neighbor_result["material_id"],
            "mp_id": neighbor_result["mp_id"],
            "pretty_formula": neighbor_result["pretty_formula"],
            "formula": neighbor_result["formula"],
            "material_type": neighbor_result["material_type"],
            "is_stable": neighbor_result["is_stable"],
            "energy_above_hull": neighbor_result["energy_above_hull"],
            "criticality_score": source_criticality_score,
            "similar_materials": similar_materials,
        }

    def _empty_similarity_response(self, material_id: int) -> dict:
        return {
            "material_id": material_id,
            "mp_id": None,
            "pretty_formula": None,
            "formula": None,
            "material_type": None,
            "is_stable": None,
            "energy_above_hull": None,
            "criticality_score": None,
            "similar_materials": [],
        }

    
    def _similarity_ranking_key(
        self,
        item: dict,
    ) -> tuple[float, bool, float, int]:
        criticality_delta = item["criticality_delta"]

        return (
            item["similarity_score"],
            criticality_delta is not None,
            (
                -abs(criticality_delta)
                if criticality_delta is not None
                else 0.0
            ),
            -item["material_id"],
        )


    def _calculate_criticality_delta(
        self,
        source_criticality_score: float | None,
        neighbor_criticality_score: float | None,
    ) -> float | None:
        if source_criticality_score is None or neighbor_criticality_score is None:
            return None

        return round(neighbor_criticality_score - source_criticality_score, 2)

    def _criticality_direction(self, criticality_delta: float | None) -> str:
        if criticality_delta is None:
            return "UNKNOWN"

        if criticality_delta < 0:
            return "LOWER_CRITICALITY"

        if criticality_delta > 0:
            return "HIGHER_CRITICALITY"

        return "SAME_CRITICALITY"

    def _calculate_similarity_score(self, neighbor: dict) -> float:
        score = 0.0

        score += neighbor["shared_element_count"] * 20
        score += neighbor["shared_application_count"] * 30

        if neighbor["is_stable"]:
            score += 10

        energy_above_hull = neighbor["energy_above_hull"]

        if energy_above_hull is not None:
            if energy_above_hull <= 0.01:
                score += 10
            elif energy_above_hull <= 0.05:
                score += 5

        return round(score, 2)

    def _build_reason_summary(
        self,
        neighbor: dict,
        criticality_delta: float | None = None,
    ) -> str:
        reasons = []

        if neighbor["shared_element_count"] > 0:
            reasons.append(f"shares {neighbor['shared_element_count']} element(s)")

        if neighbor["shared_application_count"] > 0:
            reasons.append(
                f"shares {neighbor['shared_application_count']} application(s)"
            )

        if neighbor["is_stable"]:
            reasons.append("is stable")

        if neighbor["energy_above_hull"] is not None:
            reasons.append(f"energy above hull: {neighbor['energy_above_hull']}")

        if criticality_delta is not None:
            if criticality_delta < 0:
                reasons.append(f"lower criticality by {abs(criticality_delta)}")
            elif criticality_delta > 0:
                reasons.append(f"higher criticality by {criticality_delta}")
            else:
                reasons.append("same criticality")

        return "; ".join(reasons)