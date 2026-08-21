from sqlalchemy.orm import Session

from app.services.material.similarity_service import MaterialSimilarityService
from app.services.scenario_policy import (
    ScenarioPolicy,
    ScenarioPolicyEvaluator,
)

CRITICALITY_DELTA_MULTIPLIER = 2.0


class MaterialRecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.similarity_service = MaterialSimilarityService(db)

    def get_recommendations(
        self,
        material_id: int,
        limit: int | None = 10,
        prefer_lower_criticality: bool = False,
    ) -> dict:
        similarity_result = self.similarity_service.get_similar_materials(
            material_id=material_id,
            limit=None,
        )

        if similarity_result["mp_id"] is None:
            return self._empty_recommendation_response(
                material_id,
                prefer_lower_criticality,
            )

        recommendations = []

        for candidate in similarity_result["similar_materials"]:
            recommendation_score = self._calculate_recommendation_score(
                candidate=candidate,
                prefer_lower_criticality=prefer_lower_criticality,
            )

            recommendations.append(
                {
                    "material_id": candidate["material_id"],
                    "mp_id": candidate["mp_id"],
                    "pretty_formula": candidate["pretty_formula"],
                    "formula": candidate["formula"],
                    "material_type": candidate["material_type"],
                    "is_stable": candidate["is_stable"],
                    "energy_above_hull": candidate["energy_above_hull"],
                    "stability_band": candidate.get(
                        "stability_band",
                        "unknown",
                    ),
                    "stability_evidence_basis": candidate.get(
                        "stability_evidence_basis",
                        "unavailable",
                    ),
                    "stability_evidence_complete": candidate.get(
                        "stability_evidence_complete",
                        False,
                    ),
                    "stability_source_consistency": candidate.get(
                        "stability_source_consistency",
                        "not_comparable",
                    ),
                    "stability_score_contribution": candidate.get(
                        "stability_score_contribution",
                        0.0,
                    ),
                    "similarity_score": candidate["similarity_score"],
                    "criticality_score": candidate["criticality_score"],
                    "criticality_delta": candidate["criticality_delta"],
                    "criticality_direction": candidate["criticality_direction"],
                    "shared_element_count": candidate["shared_element_count"],
                    "shared_application_count": candidate["shared_application_count"],
                    "relationship_types": candidate["relationship_types"],
                    "recommendation_score": recommendation_score,
                    "recommendation_reason": self._build_recommendation_reason(
                        candidate=candidate,
                        recommendation_score=recommendation_score,
                        prefer_lower_criticality=prefer_lower_criticality,
                    ),
                }
            )

        recommendations.sort(
            key=lambda item: (
                -item["recommendation_score"],
                item["material_id"],
            ),
        )

        returned_recommendations = (
            recommendations[:limit]
            if limit is not None
            else recommendations
        )

        return {
            "material_id": similarity_result["material_id"],
            "mp_id": similarity_result["mp_id"],
            "pretty_formula": similarity_result["pretty_formula"],
            "formula": similarity_result["formula"],
            "criticality_score": similarity_result["criticality_score"],
            "ranking_policy": self._ranking_policy(
                prefer_lower_criticality
            ),
            "candidate_pool_count": len(recommendations),
            "returned_count": len(returned_recommendations),
            "recommendations": returned_recommendations,
        }

    def get_scenario_recommendations(
        self,
        material_id: int,
        element: str,
        supply_risk_multiplier: float = 1.0,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        limit: int = 10,
        prefer_lower_criticality: bool = False,
    ) -> dict:
        base_result = self.get_recommendations(
            material_id=material_id,
            limit=None,
            prefer_lower_criticality=prefer_lower_criticality,
        )

        if base_result["mp_id"] is None:
            return self._empty_scenario_recommendation_response(
                material_id=material_id,
                element=element,
                supply_risk_multiplier=supply_risk_multiplier,
                avoid_element=avoid_element,
                prefer_element=prefer_element,
                limit=limit,
                prefer_lower_criticality=prefer_lower_criticality,
            )

        policy = ScenarioPolicy(
            element=element,
            supply_risk_multiplier=supply_risk_multiplier,
            avoid_elements=[avoid_element] if avoid_element else [],
            prefer_elements=[prefer_element] if prefer_element else [],
        )

        evaluator = ScenarioPolicyEvaluator()
        scenario_recommendations = []

        for recommendation in base_result["recommendations"]:
            policy_result = evaluator.evaluate(
                recommendation_score=recommendation["recommendation_score"],
                candidate_formula=recommendation["formula"],
                policy=policy,
            )

            scenario_recommendations.append(
                {
                    **recommendation,
                    "scenario_score": policy_result.scenario_score,
                    "scenario_delta": policy_result.scenario_delta,
                    "scenario_reason": policy_result.scenario_reason,
                }
            )

        scenario_recommendations.sort(
            key=lambda item: (
                -item["scenario_score"],
                item["material_id"],
            ),
        )

        return {
            "material_id": base_result["material_id"],
            "mp_id": base_result["mp_id"],
            "pretty_formula": base_result["pretty_formula"],
            "formula": base_result["formula"],
            "criticality_score": base_result["criticality_score"],
            "ranking_policy": base_result["ranking_policy"],
            "candidate_pool_count": len(scenario_recommendations),
            "returned_count": len(scenario_recommendations[:limit]),
            "scenario": self._build_scenario_payload(
                element=element,
                supply_risk_multiplier=supply_risk_multiplier,
                avoid_element=avoid_element,
                prefer_element=prefer_element,
                limit=limit,
            ),
            "recommendations": scenario_recommendations[:limit],
        }

    def _calculate_recommendation_score(
        self,
        candidate: dict,
        prefer_lower_criticality: bool,
    ) -> float:
        score = candidate["similarity_score"]

        criticality_delta = candidate["criticality_delta"]

        if prefer_lower_criticality and criticality_delta is not None:
            if criticality_delta < 0:
                score += abs(criticality_delta) * CRITICALITY_DELTA_MULTIPLIER
            elif criticality_delta > 0:
                score -= criticality_delta * CRITICALITY_DELTA_MULTIPLIER

        return round(score, 2)

    def _build_recommendation_reason(
        self,
        candidate: dict,
        recommendation_score: float,
        prefer_lower_criticality: bool,
    ) -> str:
        reasons = [f"similarity score {candidate['similarity_score']}"]

        criticality_direction = candidate["criticality_direction"]
        criticality_delta = candidate["criticality_delta"]

        criticality_reason: str | None = None

        if (
            criticality_direction == "LOWER_CRITICALITY"
            and criticality_delta is not None
        ):
            criticality_reason = (
                f"lower criticality by {abs(criticality_delta)}"
            )
        elif (
            criticality_direction == "HIGHER_CRITICALITY"
            and criticality_delta is not None
        ):
            criticality_reason = (
                f"higher criticality by {abs(criticality_delta)}"
            )
        elif criticality_direction == "SAME_CRITICALITY":
            criticality_reason = "same criticality"

        if criticality_reason and prefer_lower_criticality:
            reasons.append(criticality_reason)

        similarity_basis = []

        if candidate["shared_element_count"] > 0:
            similarity_basis.append(
                f"shares {candidate['shared_element_count']} element(s)"
            )

        if candidate["shared_application_count"] > 0:
            similarity_basis.append(
                f"shares {candidate['shared_application_count']} application(s)"
            )

        if similarity_basis:
            reasons.append(
                f"similarity basis: {', '.join(similarity_basis)}"
            )

        stability_contribution = candidate.get(
            "stability_score_contribution",
            0.0,
        )
        if stability_contribution > 0:
            reasons.append(
                "stability contribution already included in similarity "
                f"score: {stability_contribution}"
            )

        if candidate.get("stability_source_consistency") == "inconsistent":
            reasons.append("context: imported stability sources are inconsistent")

        reasons.append(f"recommendation score {recommendation_score}")

        if criticality_reason and not prefer_lower_criticality:
            reasons.append(f"context: {criticality_reason}")

        return "; ".join(reasons)

    def _empty_recommendation_response(
        self,
        material_id: int,
        prefer_lower_criticality: bool = False,
    ) -> dict:
        return {
            "material_id": material_id,
            "mp_id": None,
            "pretty_formula": None,
            "formula": None,
            "criticality_score": None,
            "ranking_policy": self._ranking_policy(
                prefer_lower_criticality
            ),
            "candidate_pool_count": 0,
            "returned_count": 0,
            "recommendations": [],
        }

    def _empty_scenario_recommendation_response(
        self,
        material_id: int,
        element: str,
        supply_risk_multiplier: float,
        avoid_element: str | None,
        prefer_element: str | None,
        limit: int,
        prefer_lower_criticality: bool,
    ) -> dict:
        return {
            **self._empty_recommendation_response(
                material_id,
                prefer_lower_criticality,
            ),
            "ranking_policy": self._ranking_policy(
                prefer_lower_criticality
            ),
            "scenario": self._build_scenario_payload(
                element=element,
                supply_risk_multiplier=supply_risk_multiplier,
                avoid_element=avoid_element,
                prefer_element=prefer_element,
                limit=limit,
            ),
        }

    def _build_scenario_payload(
        self,
        element: str,
        supply_risk_multiplier: float,
        avoid_element: str | None,
        prefer_element: str | None,
        limit: int,
    ) -> dict:
        return {
            "element": element,
            "supply_risk_multiplier": supply_risk_multiplier,
            "avoid_element": avoid_element,
            "prefer_element": prefer_element,
            "limit": limit,
        }

    def _ranking_policy(
        self,
        prefer_lower_criticality: bool,
    ) -> dict:
        return {
            "prefer_lower_criticality": prefer_lower_criticality,
            "criticality_delta_multiplier": (
                CRITICALITY_DELTA_MULTIPLIER
                if prefer_lower_criticality
                else 0.0
            ),
            "candidate_pool": "all_similar_materials_before_limit",
            "final_tie_breaker": "material_id_asc",
            "stability_policy": (
                "inherited_from_similarity_not_reapplied"
            ),
        }