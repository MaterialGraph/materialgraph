from app.core.database import SessionLocal
from app.models.application import Application
from app.models.element import Element


ELEMENTS = [
    {"symbol": "Li", "name": "Lithium", "atomic_number": 3, "category": "alkali metal"},
    {"symbol": "Na", "name": "Sodium", "atomic_number": 11, "category": "alkali metal"},
    {"symbol": "Mg", "name": "Magnesium", "atomic_number": 12, "category": "alkaline earth metal"},
    {"symbol": "Fe", "name": "Iron", "atomic_number": 26, "category": "transition metal"},
    {"symbol": "Mn", "name": "Manganese", "atomic_number": 25, "category": "transition metal"},
    {"symbol": "Co", "name": "Cobalt", "atomic_number": 27, "category": "transition metal"},
    {"symbol": "Ni", "name": "Nickel", "atomic_number": 28, "category": "transition metal"},
    {"symbol": "P", "name": "Phosphorus", "atomic_number": 15, "category": "nonmetal"},
    {"symbol": "O", "name": "Oxygen", "atomic_number": 8, "category": "nonmetal"},
]

APPLICATIONS = [
    {
        "name": "Battery Cathode",
        "description": "Candidate materials used as cathodes in battery systems.",
    },
    {
        "name": "Battery Anode",
        "description": "Candidate materials used as anodes in battery systems.",
    },
    {
        "name": "Solid Electrolyte",
        "description": "Candidate materials used as solid electrolytes in battery systems.",
    },
]

def seed_elements(db):
    for item in ELEMENTS:
        existing = db.query(Element).filter(Element.symbol == item["symbol"]).first()

        if existing:
            continue

        db.add(Element(**item))


def seed_applications(db):
    for item in APPLICATIONS:
        existing = db.query(Application).filter(Application.name == item["name"]).first()

        if existing:
            continue

        db.add(Application(**item))


def main():
    db = SessionLocal()

    try:
        seed_elements(db)
        seed_applications(db)
        db.commit()

        print("Core seed data inserted successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()