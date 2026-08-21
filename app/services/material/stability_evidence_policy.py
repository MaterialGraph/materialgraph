from dataclasses import dataclass
from typing import Literal


StabilityBand = Literal[
    "stable",
    "near_stable",
    "metastable",
    "unstable",
    "unknown",
]
StabilityEvidenceBasis = Literal[
    "energy_above_hull",
    "imported_is_stable_fallback",
    "unavailable",
]
StabilitySourceConsistency = Literal[
    "consistent",
    "inconsistent",
    "not_comparable",
]


@dataclass(frozen=True)
class StabilityEvidence:
    band: StabilityBand
    evidence_basis: StabilityEvidenceBasis
    evidence_complete: bool
    source_consistency: StabilitySourceConsistency
    stability_score: float
    quality_score_fraction: float
    similarity_score_contribution: float
    reason: str


class StabilityEvidencePolicy:
    """Convert correlated stability fields into one scoring signal.

    Energy above hull is the primary quantitative evidence when present.
    The imported stable flag is used only as a fallback when energy evidence
    is unavailable. Consumers may therefore use the assessment without
    rewarding both upstream fields independently.
    """

    @classmethod
    def assess(
        cls,
        *,
        is_stable: bool,
        energy_above_hull: float | None,
    ) -> StabilityEvidence:
        if energy_above_hull is None:
            return cls._from_stable_flag(is_stable)

        if energy_above_hull <= 0.01:
            band: StabilityBand = "stable"
            stability_score = 100.0
            quality_score_fraction = 0.70
            similarity_score_contribution = 20.0
        elif energy_above_hull <= 0.05:
            band = "near_stable"
            stability_score = 85.0
            quality_score_fraction = 0.60
            similarity_score_contribution = 15.0
        elif energy_above_hull <= 0.1:
            band = "metastable"
            stability_score = 70.0
            quality_score_fraction = 0.50
            similarity_score_contribution = 10.0
        else:
            band = "unstable"
            stability_score = 0.0
            quality_score_fraction = 0.0
            similarity_score_contribution = 0.0

        energy_indicates_stable = band == "stable"
        source_consistency: StabilitySourceConsistency = (
            "consistent"
            if is_stable == energy_indicates_stable
            else "inconsistent"
        )

        return StabilityEvidence(
            band=band,
            evidence_basis="energy_above_hull",
            evidence_complete=True,
            source_consistency=source_consistency,
            stability_score=stability_score,
            quality_score_fraction=quality_score_fraction,
            similarity_score_contribution=similarity_score_contribution,
            reason=(
                f"Stability band {band} is based on energy above hull "
                f"{energy_above_hull}."
            ),
        )

    @staticmethod
    def _from_stable_flag(is_stable: bool) -> StabilityEvidence:
        if is_stable:
            return StabilityEvidence(
                band="stable",
                evidence_basis="imported_is_stable_fallback",
                evidence_complete=False,
                source_consistency="not_comparable",
                stability_score=50.0,
                quality_score_fraction=0.35,
                similarity_score_contribution=10.0,
                reason=(
                    "Energy above hull is unavailable; the imported stable "
                    "flag is used as incomplete fallback evidence."
                ),
            )

        return StabilityEvidence(
            band="unstable",
            evidence_basis="imported_is_stable_fallback",
            evidence_complete=False,
            source_consistency="not_comparable",
            stability_score=0.0,
            quality_score_fraction=0.0,
            similarity_score_contribution=0.0,
            reason=(
                "Energy above hull is unavailable; the imported non-stable "
                "flag is used as incomplete fallback evidence."
            ),
        )