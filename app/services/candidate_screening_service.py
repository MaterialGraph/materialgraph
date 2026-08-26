from sqlalchemy.orm import Session
from app.core.logging import logger

from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.schemas.screening import (
    CandidateScreeningEvaluation,
    CandidateScreeningRequest,
    CandidateScreeningResult,
)
from app.services.material.risk_service import MaterialRiskService


DEFAULT_SCREENING_WEIGHTS = {
    "base_score": 50,
    "scarce_element_penalty": -30,
    "avoided_element_penalty": -40,
    "stable_bonus": 20,
    "near_stable_bonus": 10,
    "unstable_penalty": -15,
    "risk_penalty_multiplier": 5,
}


class CandidateScreeningService:
    def __init__(self, db: Session):
        self.db = db
        self.weights = DEFAULT_SCREENING_WEIGHTS
        self.material_risk_service = MaterialRiskService(db)

    def screen_candidates(
        self,
        request: CandidateScreeningRequest,
    ) -> list[CandidateScreeningResult]:
        materials = self.db.query(Material).all()

        results = self._screen_materials(
            materials=materials,
            request=request,
        )

        logger.info(
            "Screened {} candidate materials with scarce_elements={} "
            "avoid_elements={}",
            len(results),
            request.scarce_elements,
            request.avoid_elements,
        )

        return results

    def evaluate_candidate_ids(
        self,
        request: CandidateScreeningRequest,
        material_ids: list[int],
    ) -> list[CandidateScreeningEvaluation]:
        requested_ids = list(dict.fromkeys(material_ids))

        if not requested_ids:
            return []

        materials = (
            self.db.query(Material)
            .filter(Material.id.in_(requested_ids))
            .all()
        )
        material_by_id = {
            material.id: material
            for material in materials
        }
        eligible_materials = [
            material
            for material in materials
            if self._filter_disposition(material, request) is None
        ]
        screened_by_id = {
            result.material_id: result
            for result in self._screen_materials(
                materials=eligible_materials,
                request=request,
            )
        }
        evaluations = []

        for material_id in requested_ids:
            material = material_by_id.get(material_id)

            if material is None:
                evaluations.append(
                    CandidateScreeningEvaluation(
                        material_id=material_id,
                        disposition="material_not_found",
                        reason="Material does not exist.",
                    )
                )
                continue

            filtered = self._filter_disposition(material, request)

            if filtered is not None:
                disposition, reason = filtered
                evaluations.append(
                    CandidateScreeningEvaluation(
                        material_id=material_id,
                        disposition=disposition,
                        reason=reason,
                    )
                )
                continue

            result = screened_by_id.get(material_id)

            if result is None:
                evaluations.append(
                    CandidateScreeningEvaluation(
                        material_id=material_id,
                        disposition="unavailable",
                        reason=(
                            "Material could not be evaluated by the "
                            "screening service."
                        ),
                    )
                )
                continue

            evaluations.append(
                CandidateScreeningEvaluation(
                    material_id=material_id,
                    disposition="eligible",
                    reason="Material satisfies the selected constraints.",
                    result=result,
                )
            )

        return evaluations

    def _screen_materials(
        self,
        *,
        materials: list[Material],
        request: CandidateScreeningRequest,
    ) -> list[CandidateScreeningResult]:
        eligible_materials = [
            material
            for material in materials
            if self._filter_disposition(material, request) is None
        ]
        material_ids = [
            material.id
            for material in eligible_materials
        ]

        risk_signals_by_id = (
            self.material_risk_service.get_material_risk_signals_bulk(
                material_ids
            )
        )
        elements_by_material_id = self._get_material_element_symbols_bulk(
            material_ids
        )

        results = []

        scarce_elements = set(request.scarce_elements)
        avoid_elements = set(request.avoid_elements)

        for material in eligible_materials:
            element_symbols = elements_by_material_id.get(material.id, set())

            score, reasons = self._score_material(
                material=material,
                element_symbols=element_symbols,
                scarce_elements=scarce_elements,
                avoid_elements=avoid_elements,
            )

            risk_signal = risk_signals_by_id.get(material.id)

            if risk_signal is None:
                risk_signal = self._unknown_risk_signal(
                    material_id=material.id,
                    element_symbols=element_symbols,
                )

            material_risk_score = risk_signal.get("risk_score")
            risk_known = risk_signal.get("risk_known", False)
            score_before_risk_penalty = score

            score, risk_penalty = self.apply_material_risk_penalty(
                score_before_risk_penalty=score_before_risk_penalty,
                material_risk_score=(
                    material_risk_score if risk_known else None
                ),
            )

            if risk_known and material_risk_score is not None:
                reasons.append(
                    f"Material risk score {material_risk_score} "
                    f"applied as penalty {round(risk_penalty, 3)}"
                )
            else:
                risk_penalty = 0.0

                reasons.append(
                    "Material risk evidence unavailable; "
                    "risk penalty not applied"
                )

            results.append(
                CandidateScreeningResult(
                    material_id=material.id,
                    mp_id=material.mp_id,
                    formula=material.formula,
                    pretty_formula=material.pretty_formula,
                    score=round(score, 3),
                    score_before_risk_penalty=round(
                        score_before_risk_penalty,
                        3,
                    ),
                    material_risk_score=material_risk_score,
                    risk_known=risk_known,
                    risk_profile_coverage=risk_signal.get(
                        "risk_profile_coverage",
                        0.0,
                    ),
                    known_risk_element_count=risk_signal.get(
                        "known_risk_element_count",
                        0,
                    ),
                    total_element_count=risk_signal.get(
                        "total_element_count",
                        len(element_symbols),
                    ),
                    risk_evidence_complete=risk_signal.get(
                        "risk_evidence_complete",
                        False,
                    ),
                    unknown_risk_elements=risk_signal.get(
                        "unknown_risk_elements",
                        [],
                    ),
                    risk_penalty=round(risk_penalty, 3),
                    elements=sorted(element_symbols),
                    contains_scarce_elements=bool(
                        element_symbols.intersection(scarce_elements)
                    ),
                    contains_avoided_elements=bool(
                        element_symbols.intersection(avoid_elements)
                    ),
                    reasons=reasons,
                )
            )

        ranked_results = sorted(
            results,
            key=self._ranking_key,
            reverse=True,
        )

        return ranked_results

    def apply_material_risk_penalty(
        self,
        *,
        score_before_risk_penalty: float,
        material_risk_score: float | None,
    ) -> tuple[float, float]:
        risk_penalty = (
            material_risk_score
            * self.weights["risk_penalty_multiplier"]
            if material_risk_score is not None
            else 0.0
        )
        score = max(
            0.0,
            min(100.0, score_before_risk_penalty - risk_penalty),
        )

        return score, risk_penalty

    @staticmethod
    def _filter_disposition(
        material: Material,
        request: CandidateScreeningRequest,
    ) -> tuple[str, str] | None:
        if request.require_stable and not material.is_stable:
            return (
                "filtered_unstable",
                "Material was excluded because stable material was required.",
            )

        if (
            request.max_energy_above_hull is not None
            and material.energy_above_hull is not None
            and material.energy_above_hull
            > request.max_energy_above_hull
        ):
            return (
                "filtered_energy_above_hull",
                "Material energy above hull exceeds the selected maximum.",
            )

        return None

    def _get_material_element_symbols_bulk(
        self,
        material_ids: list[int],
    ) -> dict[int, set[str]]:
        if not material_ids:
            return {}

        rows = (
            self.db.query(MaterialElement.material_id, Element.symbol)
            .join(MaterialElement, Element.id == MaterialElement.element_id)
            .filter(MaterialElement.material_id.in_(material_ids))
            .all()
        )

        elements_by_material_id: dict[int, set[str]] = {}
        for material_id, symbol in rows:
            elements_by_material_id.setdefault(material_id, set()).add(symbol)

        return elements_by_material_id

    def _unknown_risk_signal(
        self,
        material_id: int,
        element_symbols: set[str],
    ) -> dict:
        return {
            "material_id": material_id,
            "risk_score": None,
            "risk_known": False,
            "risk_profile_coverage": 0.0,
            "known_risk_element_count": 0,
            "total_element_count": len(element_symbols),
            "known_risk_elements": [],
            "unknown_risk_elements": sorted(element_symbols),
            "risk_evidence_complete": False,
        }


    def _decision_key(
        self,
        candidate: CandidateScreeningResult,
    ) -> tuple[float, bool, float]:
        return (
            candidate.score_before_risk_penalty,
            candidate.risk_known,
            candidate.score,
        )


    def _ranking_key(
        self,
        candidate: CandidateScreeningResult,
    ) -> tuple[float, bool, float, int]:
        return (
            *self._decision_key(candidate),
            -candidate.material_id,
        )


    def _score_material(
        self,
        material: Material,
        element_symbols: set[str],
        scarce_elements: set[str],
        avoid_elements: set[str],
    ) -> tuple[float, list[str]]:
        score = float(self.weights["base_score"])
        reasons = []

        scarce_hits = element_symbols.intersection(scarce_elements)
        avoid_hits = element_symbols.intersection(avoid_elements)

        if scarce_hits:
            score += self.weights["scarce_element_penalty"]
            reasons.append(
                f"Contains scarce element(s): {', '.join(sorted(scarce_hits))}"
            )
        else:
            reasons.append("Does not contain scarce elements")

        if avoid_hits:
            score += self.weights["avoided_element_penalty"]
            reasons.append(
                f"Contains avoided element(s): {', '.join(sorted(avoid_hits))}"
            )
        else:
            reasons.append("Does not contain avoided elements")

        if material.is_stable:
            score += self.weights["stable_bonus"]
            reasons.append("Material is stable according to Materials Project")
        elif material.energy_above_hull is not None:
            if material.energy_above_hull <= 0.05:
                score += self.weights["near_stable_bonus"]
                reasons.append("Material is near-stable")
            else:
                score += self.weights["unstable_penalty"]
                reasons.append("Material has higher energy above hull")
        else:
            reasons.append("Stability information unavailable")

        return score, reasons