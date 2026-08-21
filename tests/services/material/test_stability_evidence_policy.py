from app.services.material.stability_evidence_policy import (
    StabilityEvidencePolicy,
)


def test_energy_above_hull_is_primary_when_available():
    assessment = StabilityEvidencePolicy.assess(
        is_stable=True,
        energy_above_hull=0.04,
    )

    assert assessment.band == "near_stable"
    assert assessment.evidence_basis == "energy_above_hull"
    assert assessment.evidence_complete is True
    assert assessment.quality_score_fraction == 0.60
    assert assessment.similarity_score_contribution == 15.0


def test_stable_flag_is_fallback_when_energy_is_unavailable():
    assessment = StabilityEvidencePolicy.assess(
        is_stable=True,
        energy_above_hull=None,
    )

    assert assessment.band == "stable"
    assert assessment.evidence_basis == "imported_is_stable_fallback"
    assert assessment.evidence_complete is False
    assert assessment.source_consistency == "not_comparable"
    assert assessment.quality_score_fraction == 0.35
    assert assessment.similarity_score_contribution == 10.0


def test_correlated_fields_produce_one_stability_contribution():
    assessment = StabilityEvidencePolicy.assess(
        is_stable=True,
        energy_above_hull=0.0,
    )

    assert assessment.stability_score == 100.0
    assert assessment.quality_score_fraction == 0.70
    assert assessment.similarity_score_contribution == 20.0


def test_inconsistent_stability_sources_are_disclosed():
    assessment = StabilityEvidencePolicy.assess(
        is_stable=True,
        energy_above_hull=0.08,
    )

    assert assessment.band == "metastable"
    assert assessment.source_consistency == "inconsistent"


def test_unstable_energy_does_not_receive_stable_flag_bonus():
    assessment = StabilityEvidencePolicy.assess(
        is_stable=True,
        energy_above_hull=0.2,
    )

    assert assessment.band == "unstable"
    assert assessment.stability_score == 0.0
    assert assessment.quality_score_fraction == 0.0
    assert assessment.similarity_score_contribution == 0.0