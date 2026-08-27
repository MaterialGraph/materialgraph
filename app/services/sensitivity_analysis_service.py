from sqlalchemy.orm import Session

from app.schemas.screening import CandidateScreeningRequest
from app.schemas.sensitivity import (
    SensitivityAnalysisRequest,
    SensitivityAnalysisResult,
    SensitivityScenarioResult,
)
from app.services.candidate_screening_service import CandidateScreeningService
from app.services.material.risk_evidence_policy import (
    RISK_EVIDENCE_DIMENSIONS,
    calculate_material_risk_score,
)
from app.services.material.risk_service import MaterialRiskService


class SensitivityAnalysisService:
    RISK_SCORE_MAX = 10.0
    SCENARIO_DEFINITIONS = (
        ("supply_risk_plus_25_percent", "supply_risk", 1.25),
        ("supply_risk_plus_50_percent", "supply_risk", 1.50),
        ("geopolitical_risk_plus_25_percent", "geopolitical_risk", 1.25),
        ("geopolitical_risk_plus_50_percent", "geopolitical_risk", 1.50),
    )

    def __init__(self, db: Session):
        self.db = db
        self.screening_service = CandidateScreeningService(db)
        self.risk_service = MaterialRiskService(db)

    def analyze(
        self,
        request: SensitivityAnalysisRequest,
    ) -> SensitivityAnalysisResult | None:
        baseline_request = CandidateScreeningRequest(
            scarce_elements=["Li"],
            avoid_elements=["Co"],
            require_stable=True,
            max_energy_above_hull=0.05,
        )

        baseline_results = self.screening_service.screen_candidates(
            baseline_request
        )

        baseline = next(
            (
                result
                for result in baseline_results
                if result.material_id == request.material_id
            ),
            None,
        )

        if baseline is None:
            return None

        material_risk = self.risk_service.get_material_risk(
            baseline.material_id
        )
        supply_risk_score = self._mean_component_score(
            material_risk,
            "supply_risk_score",
        )
        geopolitical_risk_score = self._mean_component_score(
            material_risk,
            "geopolitical_risk_score",
        )

        scenarios = self._build_sensitivity_scenarios(
            baseline_score=baseline.score,
            score_before_risk_penalty=baseline.score_before_risk_penalty,
            baseline_material_risk_score=baseline.material_risk_score,
            material_risk=material_risk,
            baseline_supply_risk_score=supply_risk_score,
            baseline_geopolitical_risk_score=geopolitical_risk_score,
        )

        known_deltas = [
            abs(item.score_delta)
            for item in scenarios
            if item.score_delta is not None
        ]
        sensitivity_level = (
            self._classify_sensitivity(max(known_deltas))
            if known_deltas
            else "UNKNOWN"
        )

        return SensitivityAnalysisResult(
            material_id=baseline.material_id,
            formula=baseline.pretty_formula,
            baseline_score=baseline.score,
            baseline_material_risk_score=baseline.material_risk_score,
            baseline_supply_risk_score=supply_risk_score,
            baseline_geopolitical_risk_score=geopolitical_risk_score,
            selected_risk_profile_ids=(
                getattr(material_risk, "selected_profile_ids", [])
                if material_risk is not None
                else []
            ),
            selected_risk_profile_years=(
                getattr(material_risk, "selected_profile_years", [])
                if material_risk is not None
                else []
            ),
            selected_risk_profile_sources=(
                getattr(material_risk, "selected_profile_sources", [])
                if material_risk is not None
                else []
            ),
            sensitivity_level=sensitivity_level,
            scenarios=scenarios,
        )

    def _build_sensitivity_scenarios(
        self,
        baseline_score: float,
        score_before_risk_penalty: float,
        baseline_material_risk_score: float | None,
        material_risk,
        baseline_supply_risk_score: float | None,
        baseline_geopolitical_risk_score: float | None,
    ) -> list[SensitivityScenarioResult]:
        component_scores = {
            "supply_risk": baseline_supply_risk_score,
            "geopolitical_risk": baseline_geopolitical_risk_score,
        }
        results = []

        for name, risk_dimension, multiplier in self.SCENARIO_DEFINITIONS:
            baseline_component = component_scores[risk_dimension]

            if baseline_component is None:
                results.append(
                    SensitivityScenarioResult(
                        scenario=name,
                        risk_dimension=risk_dimension,
                        baseline_component_score=None,
                        adjusted_component_score=None,
                        adjusted_material_risk_score=None,
                        material_risk_delta=None,
                        adjusted_score=None,
                        score_delta=None,
                    )
                )
                continue

            attribute = self._risk_attribute(risk_dimension)
            adjusted_component = self._mean_adjusted_component_score(
                material_risk=material_risk,
                attribute=attribute,
                multiplier=multiplier,
            )
            adjusted_material_risk = self._adjusted_material_risk_score(
                material_risk=material_risk,
                attribute=attribute,
                multiplier=multiplier,
            )

            if adjusted_material_risk is None:
                adjusted_score = None
                material_risk_delta = None
            else:
                adjusted_score, _ = (
                    self.screening_service.apply_material_risk_penalty(
                        score_before_risk_penalty=score_before_risk_penalty,
                        material_risk_score=adjusted_material_risk,
                    )
                )
                material_risk_delta = (
                    adjusted_material_risk - baseline_material_risk_score
                    if baseline_material_risk_score is not None
                    else None
                )

            results.append(
                SensitivityScenarioResult(
                    scenario=name,
                    risk_dimension=risk_dimension,
                    baseline_component_score=round(baseline_component, 3),
                    adjusted_component_score=adjusted_component,
                    adjusted_material_risk_score=adjusted_material_risk,
                    material_risk_delta=(
                        round(material_risk_delta, 3)
                        if material_risk_delta is not None
                        else None
                    ),
                    adjusted_score=(
                        round(adjusted_score, 3)
                        if adjusted_score is not None
                        else None
                    ),
                    score_delta=(
                        round(adjusted_score - baseline_score, 3)
                        if adjusted_score is not None
                        else None
                    ),
                )
            )

        return results

    def _mean_component_score(
        self,
        material_risk,
        attribute: str,
    ) -> float | None:
        if material_risk is None:
            return None

        values = [
            getattr(element_risk, attribute)
            for element_risk in material_risk.element_risks
            if getattr(element_risk, attribute) is not None
        ]

        if not values:
            return None

        return round(sum(values) / len(values), 3)

    def _mean_adjusted_component_score(
        self,
        *,
        material_risk,
        attribute: str,
        multiplier: float,
    ) -> float | None:
        if material_risk is None:
            return None

        adjusted_values = [
            min(
                self.RISK_SCORE_MAX,
                getattr(element_risk, attribute) * multiplier,
            )
            for element_risk in material_risk.element_risks
            if getattr(element_risk, attribute) is not None
        ]

        if not adjusted_values:
            return None

        return round(sum(adjusted_values) / len(adjusted_values), 3)

    def _adjusted_material_risk_score(
        self,
        *,
        material_risk,
        attribute: str,
        multiplier: float,
    ) -> float | None:
        if material_risk is None:
            return None

        element_dimension_values = []

        for element_risk in material_risk.element_risks:
            values = []

            for dimension in RISK_EVIDENCE_DIMENSIONS:
                value = getattr(element_risk, dimension)

                if dimension == attribute and value is not None:
                    value = min(self.RISK_SCORE_MAX, value * multiplier)

                values.append(value)

            element_dimension_values.append(values)

        return calculate_material_risk_score(element_dimension_values)

    @staticmethod
    def _risk_attribute(risk_dimension: str) -> str:
        return f"{risk_dimension}_score"

    def _classify_sensitivity(self, max_delta: float) -> str:
        if max_delta >= 15:
            return "HIGH"
        if max_delta >= 7:
            return "MEDIUM"
        return "LOW"