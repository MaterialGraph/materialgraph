MG_DE_005_CHEMICAL_SYSTEMS = (
    *(
        f"{mobile}-{metal}-O"
        for mobile in ("Li", "Na", "Mg", "K", "Ca")
        for metal in ("Fe", "Mn", "Co", "Ni")
    ),
    *(
        f"{mobile}-{metal}-P-O"
        for mobile in ("Li", "Na", "Mg")
        for metal in ("Fe", "Mn", "Co", "Ni")
    ),
    *(
        f"{mobile}-{metal}-S"
        for mobile in ("Li", "Na")
        for metal in ("Fe", "Mn", "Co", "Ni")
    ),
    *(
        f"{mobile}-{metal}-Si-O"
        for mobile in ("Li", "Na")
        for metal in ("Fe", "Mn", "Co", "Ni")
    ),
)

MG_DE_005_REQUIRED_ELEMENTS = (
    "Ca",
    "Co",
    "Fe",
    "K",
    "Li",
    "Mg",
    "Mn",
    "Na",
    "Ni",
    "O",
    "P",
    "S",
    "Si",
)

MG_DE_005_MINIMUM_MATERIALS = 500
MG_DE_005_MAXIMUM_MATERIALS = 3_000
MG_DE_005_MAXIMUM_SOURCE_RECORDS = 5_000
MG_DE_005_MAXIMUM_ENERGY_ABOVE_HULL = 0.1
MG_DE_005_MINIMUM_PROPERTY_COVERAGE = 0.95
