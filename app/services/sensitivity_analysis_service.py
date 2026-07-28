from sqlalchemy.orm import Session

from app.schemas.screening import CandidateScreeningRequest
from app.schemas.sensitivity import (
    SensitivityAnalysisRequest,
    SensitivityAnalysisResult,
    SensitivityScenarioResult,
)
from app.services.candidate_screening_service import CandidateScreeningService
from app.services.material.risk_service import MaterialRiskService


class SensitivityAnalysisService:
    RISK_PENALTY_WEIGHT = 5.0
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
            sensitivity_level=sensitivity_level,
            scenarios=scenarios,
        )

    def _build_sensitivity_scenarios(
        self,
        baseline_score: float,
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
                        adjusted_score=None,
                        score_delta=None,
                    )
                )
                continue

            adjusted_component = baseline_component * multiplier
            penalty_delta = (
                adjusted_component - baseline_component
            ) * self.RISK_PENALTY_WEIGHT
            adjusted_score = max(0.0, baseline_score - penalty_delta)

            results.append(
                SensitivityScenarioResult(
                    scenario=name,
                    risk_dimension=risk_dimension,
                    baseline_component_score=round(baseline_component, 3),
                    adjusted_component_score=round(adjusted_component, 3),
                    adjusted_score=round(adjusted_score, 3),
                    score_delta=round(adjusted_score - baseline_score, 3),
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

    def _classify_sensitivity(self, max_delta: float) -> str:
        if max_delta >= 15:
            return "HIGH"
        if max_delta >= 7:
            return "MEDIUM"
        return "LOW"