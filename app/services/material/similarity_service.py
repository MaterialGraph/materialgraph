from sqlalchemy.orm import Session

from app.services.material.criticality_service import MaterialCriticalityService
from app.services.material.neighbor_service import MaterialNeighborService
from app.services.material.stability_evidence_policy import (
    StabilityEvidence,
    StabilityEvidencePolicy,
)


class MaterialSimilarityService:
    def __init__(self, db: Session):
        self.db = db
        self.neighbor_service = MaterialNeighborService(db)
        self.criticality_service = MaterialCriticalityService(db)

    def get_similar_materials(
        self,
        material_id: int,
        limit: int | None = 10,
    ) -> dict:
        neighbor_result = self.neighbor_service.get_neighbors(material_id)

        if neighbor_result["mp_id"] is None:
            return self._empty_similarity_response(material_id)

        neighbors = neighbor_result["neighbors"]

        criticality_by_material_id = (
            self.criticality_service.get_material_criticality_bulk(
                material_ids=[
                    material_id,
                    *[
                        neighbor["material_id"]
                        for neighbor in neighbors
                    ],
                ]
            )
        )

        source_criticality_score = criticality_by_material_id[
            material_id
        ]["criticality_score"]

        similar_materials = []

        for neighbor in neighbors:
            neighbor_material_id = neighbor["material_id"]
            stability_evidence = StabilityEvidencePolicy.assess(
                is_stable=neighbor["is_stable"],
                energy_above_hull=neighbor["energy_above_hull"],
            )

            similarity_score = self._calculate_similarity_score(
                neighbor,
                stability_evidence=stability_evidence,
            )

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
                    "stability_band": stability_evidence.band,
                    "stability_evidence_basis": (
                        stability_evidence.evidence_basis
                    ),
                    "stability_evidence_complete": (
                        stability_evidence.evidence_complete
                    ),
                    "stability_source_consistency": (
                        stability_evidence.source_consistency
                    ),
                    "stability_score_contribution": (
                        stability_evidence.similarity_score_contribution
                    ),
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

        returned_materials = (
            similar_materials[:limit]
            if limit is not None
            else similar_materials
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
            "ranking_policy": self._ranking_policy(),
            "candidate_pool_count": len(similar_materials),
            "returned_count": len(returned_materials),
            "similar_materials": returned_materials,
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
            "ranking_policy": self._ranking_policy(),
            "candidate_pool_count": 0,
            "returned_count": 0,
            "similar_materials": [],
        }

    def _ranking_policy(self) -> dict:
        return {
            "primary": "similarity_score_desc",
            "criticality_tie_breaker": (
                "known_then_smallest_absolute_delta"
            ),
            "final_tie_breaker": "material_id_asc",
            "candidate_pool": "all_structured_neighbors_before_limit",
            "stability_policy": "single_energy_primary_signal",
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

    def _calculate_similarity_score(
        self,
        neighbor: dict,
        *,
        stability_evidence: StabilityEvidence | None = None,
    ) -> float:
        score = 0.0

        score += neighbor["shared_element_count"] * 20
        score += neighbor["shared_application_count"] * 30

        if stability_evidence is None:
            stability_evidence = StabilityEvidencePolicy.assess(
                is_stable=neighbor["is_stable"],
                energy_above_hull=neighbor["energy_above_hull"],
            )

        score += stability_evidence.similarity_score_contribution

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

        stability_evidence = StabilityEvidencePolicy.assess(
            is_stable=neighbor["is_stable"],
            energy_above_hull=neighbor["energy_above_hull"],
        )
        reasons.append(stability_evidence.reason)

        if stability_evidence.source_consistency == "inconsistent":
            reasons.append("imported stability sources are inconsistent")

        if criticality_delta is not None:
            if criticality_delta < 0:
                reasons.append(f"lower criticality by {abs(criticality_delta)}")
            elif criticality_delta > 0:
                reasons.append(f"higher criticality by {criticality_delta}")
            else:
                reasons.append("same criticality")

        return "; ".join(reasons)