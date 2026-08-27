from sqlalchemy.orm import Session

from app.models.material import Material
from app.services.material.criticality_service import MaterialCriticalityService
from app.services.material.risk_service import MaterialRiskService
from app.services.material.stability_evidence_policy import (
    StabilityEvidencePolicy,
)


class MaterialQualityService:
    QUALITY_SCORE_MAX = 15.0

    def __init__(self, db: Session):
        self.db = db
        self.criticality_service = MaterialCriticalityService(db)
        self.risk_service = MaterialRiskService(db)
        self._quality_cache: dict[int, dict] = {}

    def get_material_quality(self, material_id: int) -> dict:
        if material_id in self._quality_cache:
            return self._quality_cache[material_id]

        material = self.db.get(Material, material_id)

        if material is None:
            quality = self._empty_quality(material_id)
            self._quality_cache[material_id] = quality
            return quality

        criticality = self.criticality_service.get_material_criticality(material_id)
        criticality_score = criticality.get("criticality_score")

        risk_signal = self.risk_service.get_material_risk_signal(material_id)

        quality = self._build_quality_response(
            material=material,
            criticality_score=criticality_score,
            risk_signal=risk_signal,
            criticality_composition_evidence_status=criticality.get(
                "composition_evidence_status",
                "unavailable",
            ),
            criticality_composition_fraction_coverage=criticality.get(
                "composition_fraction_coverage",
                0.0,
            ),
            criticality_composition_evidence_complete=criticality.get(
                "composition_evidence_complete",
                False,
            ),
        )

        self._quality_cache[material_id] = quality
        return quality

    def get_material_quality_bulk(
        self,
        material_ids: list[int],
    ) -> dict[int, dict]:
        unique_ids = list(dict.fromkeys(material_ids))

        if not unique_ids:
            return {}

        missing_ids = [
            material_id
            for material_id in unique_ids
            if material_id not in self._quality_cache
        ]

        if missing_ids:
            materials = (
                self.db.query(Material)
                .filter(Material.id.in_(missing_ids))
                .all()
            )

            materials_by_id = {
                material.id: material
                for material in materials
            }

            criticality_by_id = (
                self.criticality_service.get_material_criticality_bulk(
                    missing_ids
                )
            )

            risk_signals_by_id = (
                self.risk_service.get_material_risk_signals_bulk(
                    missing_ids
                )
            )

            for material_id in missing_ids:
                material = materials_by_id.get(material_id)

                if material is None:
                    self._quality_cache[material_id] = self._empty_quality(
                        material_id
                    )
                    continue

                criticality = criticality_by_id.get(material_id, {})
                criticality_score = criticality.get("criticality_score")
                risk_signal = risk_signals_by_id.get(
                    material_id,
                    self.risk_service._unknown_risk_signal(
                        material_id=material_id,
                        total_element_count=0,
                    ),
                )

                self._quality_cache[material_id] = self._build_quality_response(
                    material=material,
                    criticality_score=criticality_score,
                    risk_signal=risk_signal,
                    criticality_composition_evidence_status=criticality.get(
                        "composition_evidence_status",
                        "unavailable",
                    ),
                    criticality_composition_fraction_coverage=criticality.get(
                        "composition_fraction_coverage",
                        0.0,
                    ),
                    criticality_composition_evidence_complete=criticality.get(
                        "composition_evidence_complete",
                        False,
                    ),
                )

        return {
            material_id: self._quality_cache[material_id]
            for material_id in unique_ids
        }

    def get_material_quality_score(self, material_id: int) -> float:
        return self.get_material_quality(material_id)["quality_score"]

    def _build_quality_response(
        self,
        material: Material,
        criticality_score: float | None,
        risk_signal: dict,
        criticality_composition_evidence_status: str = "unavailable",
        criticality_composition_fraction_coverage: float = 0.0,
        criticality_composition_evidence_complete: bool = False,
    ) -> dict:
        risk_score = risk_signal.get("risk_score")
        risk_known = risk_signal.get("risk_known", False)
        risk_evidence_complete = risk_signal.get("risk_evidence_complete", False)

        stability_evidence = StabilityEvidencePolicy.assess(
            is_stable=material.is_stable,
            energy_above_hull=material.energy_above_hull,
        )

        quality_score = self._calculate_quality_score(
            is_stable=material.is_stable,
            energy_above_hull=material.energy_above_hull,
            criticality_score=criticality_score,
            risk_score=risk_score,
            risk_known=risk_known,
            risk_evidence_complete=risk_evidence_complete,
        )
        criticality_quality_contribution = (
            self._calculate_criticality_quality_contribution(
                criticality_score
            )
        )
        risk_quality_contribution = (
            self._calculate_risk_evidence_quality_contribution(
                risk_score=risk_score,
                risk_known=risk_known,
                risk_evidence_complete=risk_evidence_complete,
            )
        )

        return {
            "material_id": material.id,
            "stability_score": stability_evidence.stability_score,
            "stability_band": stability_evidence.band,
            "stability_evidence_basis": stability_evidence.evidence_basis,
            "stability_evidence_complete": (
                stability_evidence.evidence_complete
            ),
            "stability_source_consistency": (
                stability_evidence.source_consistency
            ),
            "stability_quality_contribution": round(
                self.QUALITY_SCORE_MAX
                * stability_evidence.quality_score_fraction,
                2,
            ),
            "energy_above_hull": material.energy_above_hull,
            "criticality_score": criticality_score,
            "criticality_quality_contribution": (
                criticality_quality_contribution
            ),
            "criticality_composition_evidence_status": (
                criticality_composition_evidence_status
            ),
            "criticality_composition_fraction_coverage": (
                criticality_composition_fraction_coverage
            ),
            "criticality_composition_evidence_complete": (
                criticality_composition_evidence_complete
            ),
            "risk_score": risk_score,
            "risk_quality_contribution": risk_quality_contribution,
            "risk_known": risk_known,
            "risk_profile_coverage": risk_signal.get("risk_profile_coverage", 0.0),
            "risk_complete_profile_coverage": risk_signal.get(
                "risk_complete_profile_coverage",
                0.0,
            ),
            "risk_dimension_coverage": risk_signal.get(
                "risk_dimension_coverage",
                0.0,
            ),
            "known_risk_element_count": risk_signal.get("known_risk_element_count", 0),
            "complete_risk_profile_element_count": risk_signal.get(
                "complete_risk_profile_element_count",
                0,
            ),
            "partial_risk_profile_element_count": risk_signal.get(
                "partial_risk_profile_element_count",
                0,
            ),
            "total_element_count": risk_signal.get("total_element_count", 0),
            "risk_evidence_complete": risk_signal.get("risk_evidence_complete", False),
            "unknown_risk_elements": risk_signal.get("unknown_risk_elements", []),
            "partial_risk_profile_elements": risk_signal.get(
                "partial_risk_profile_elements",
                [],
            ),
            "risk_evidence_basis": risk_signal.get("evidence_basis"),
            "risk_evidence_dimensions": risk_signal.get(
                "risk_evidence_dimensions",
                [],
            ),
            "risk_aggregation_method": risk_signal.get("aggregation_method"),
            "quality_score": quality_score,
        }

    def _calculate_stability_score(
        self,
        is_stable: bool,
        energy_above_hull: float | None,
    ) -> float:
        return StabilityEvidencePolicy.assess(
            is_stable=is_stable,
            energy_above_hull=energy_above_hull,
        ).stability_score

    def _calculate_quality_score(
        self,
        is_stable: bool,
        energy_above_hull: float | None,
        criticality_score: float | None,
        risk_score: float | None,
        risk_known: bool,
        risk_evidence_complete: bool,
    ) -> float:
        stability_evidence = StabilityEvidencePolicy.assess(
            is_stable=is_stable,
            energy_above_hull=energy_above_hull,
        )
        score = (
            self.QUALITY_SCORE_MAX
            * stability_evidence.quality_score_fraction
        )

        score += self._calculate_risk_quality_score(
            criticality_score=criticality_score,
            risk_score=risk_score,
            risk_known=risk_known,
            risk_evidence_complete=risk_evidence_complete,
        )

        return round(min(score, self.QUALITY_SCORE_MAX), 2)

    def _calculate_risk_quality_score(
        self,
        criticality_score: float | None,
        risk_score: float | None,
        risk_known: bool,
        risk_evidence_complete: bool,
    ) -> float:
        return (
            self._calculate_criticality_quality_contribution(
                criticality_score
            )
            + self._calculate_risk_evidence_quality_contribution(
                risk_score=risk_score,
                risk_known=risk_known,
                risk_evidence_complete=risk_evidence_complete,
            )
        )

    def _calculate_criticality_quality_contribution(
        self,
        criticality_score: float | None,
    ) -> float:
        if criticality_score is None:
            return 0.0
        if criticality_score <= 30:
            return self.QUALITY_SCORE_MAX * 0.15
        if criticality_score <= 60:
            return self.QUALITY_SCORE_MAX * 0.08
        return 0.0

    def _calculate_risk_evidence_quality_contribution(
        self,
        *,
        risk_score: float | None,
        risk_known: bool,
        risk_evidence_complete: bool,
    ) -> float:
        if not (
            risk_known
            and risk_evidence_complete
            and risk_score is not None
        ):
            return 0.0
        if risk_score <= 3:
            return self.QUALITY_SCORE_MAX * 0.15
        if risk_score <= 6:
            return self.QUALITY_SCORE_MAX * 0.08
        return 0.0

    def _empty_quality(self, material_id: int) -> dict:
        return {
            "material_id": material_id,
            "stability_score": 0.0,
            "stability_band": "unknown",
            "stability_evidence_basis": "unavailable",
            "stability_evidence_complete": False,
            "stability_source_consistency": "not_comparable",
            "stability_quality_contribution": 0.0,
            "energy_above_hull": None,
            "criticality_score": None,
            "criticality_quality_contribution": 0.0,
            "criticality_composition_evidence_status": "unavailable",
            "criticality_composition_fraction_coverage": 0.0,
            "criticality_composition_evidence_complete": False,
            "risk_score": None,
            "risk_quality_contribution": 0.0,
            "risk_known": False,
            "risk_profile_coverage": 0.0,
            "risk_complete_profile_coverage": 0.0,
            "risk_dimension_coverage": 0.0,
            "known_risk_element_count": 0,
            "complete_risk_profile_element_count": 0,
            "partial_risk_profile_element_count": 0,
            "total_element_count": 0,
            "risk_evidence_complete": False,
            "unknown_risk_elements": [],
            "partial_risk_profile_elements": [],
            "risk_evidence_basis": None,
            "risk_evidence_dimensions": [],
            "risk_aggregation_method": None,
            "quality_score": 0.0,
        }