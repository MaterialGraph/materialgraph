from app.core.database import SessionLocal
from app.models.element import Element
from app.models.element_risk_profile import ElementRiskProfile


YEAR = 2026
SOURCE = "materialgraph_canonical_risk_profile_v1"
SCORE_FIELDS = (
    "abundance_score",
    "supply_risk_score",
    "toxicity_score",
    "recyclability_score",
    "geopolitical_risk_score",
)

RISK_DATA = {
    "Li": {
        "abundance_score": 4,
        "supply_risk_score": 8,
        "toxicity_score": 2,
        "recyclability_score": 6,
        "geopolitical_risk_score": 8,
    },
    "Co": {
        "abundance_score": 2,
        "supply_risk_score": 10,
        "toxicity_score": 8,
        "recyclability_score": 6,
        "geopolitical_risk_score": 10,
    },
    "Na": {
        "abundance_score": 9,
        "supply_risk_score": 1,
        "toxicity_score": 1,
        "recyclability_score": 7,
        "geopolitical_risk_score": 1,
    },
    "Mg": {
        "abundance_score": 8,
        "supply_risk_score": 2,
        "toxicity_score": 1,
        "recyclability_score": 7,
        "geopolitical_risk_score": 2,
    },
    "Fe": {
        "abundance_score": 9,
        "supply_risk_score": 1,
        "toxicity_score": 1,
        "recyclability_score": 9,
        "geopolitical_risk_score": 1,
    },
    "Mn": {
        "abundance_score": 7,
        "supply_risk_score": 3,
        "toxicity_score": 3,
        "recyclability_score": 7,
        "geopolitical_risk_score": 3,
    },
    "P": {
        "abundance_score": 6,
        "supply_risk_score": 4,
        "toxicity_score": 2,
        "recyclability_score": 5,
        "geopolitical_risk_score": 4,
    },
    "O": {
        "abundance_score": 10,
        "supply_risk_score": 1,
        "toxicity_score": 1,
        "recyclability_score": 10,
        "geopolitical_risk_score": 1,
    },
    "Ni": {
        "abundance_score": 5,
        "supply_risk_score": 6,
        "toxicity_score": 4,
        "recyclability_score": 7,
        "geopolitical_risk_score": 6,
    },
}


def validate_risk_data() -> None:
    for symbol, scores in RISK_DATA.items():
        if set(scores) != set(SCORE_FIELDS):
            raise ValueError(f"{symbol} does not define the canonical score fields")

        for field, value in scores.items():
            if not 1 <= value <= 10:
                raise ValueError(
                    f"{symbol}.{field} must be within the canonical 1-10 scale"
                )


def seed_risk_profiles(db) -> tuple[int, int]:
    validate_risk_data()

    created = 0
    updated = 0

    for symbol, scores in RISK_DATA.items():
        element = db.query(Element).filter(Element.symbol == symbol).first()

        if element is None:
            raise ValueError(f"Cannot seed risk profile: element {symbol} not found")

        profile = (
            db.query(ElementRiskProfile)
            .filter(
                ElementRiskProfile.element_id == element.id,
                ElementRiskProfile.year == YEAR,
            )
            .first()
        )

        if profile is None:
            profile = ElementRiskProfile(
                element_id=element.id,
                year=YEAR,
                source=SOURCE,
                **scores,
            )
            db.add(profile)
            created += 1
            continue

        for field, value in scores.items():
            setattr(profile, field, value)
        profile.source = SOURCE
        updated += 1

    return created, updated


def main() -> None:
    db = SessionLocal()

    try:
        created, updated = seed_risk_profiles(db)
        db.commit()
        print(f"Created: {created}")
        print(f"Updated: {updated}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()