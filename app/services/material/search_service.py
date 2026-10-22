"""Full-dataset material search (Release 1, contract M).

Four explicit modes; nothing is auto-detected or auto-corrected:

- ``formula``: composition equality. The query is parsed and compared with
  each material's normalised composition from ``raw_data["composition"]``
  (independent of ``fraction_known``). Two compositions are equal when they
  have the same elements and every fraction agrees within ``TAU``. Identical
  compositions of different MP identities are separate matches.
- ``mp_id``: exact identifier, one record or none.
- ``chemsys``: exact element set (``Li-Fe-P-O``).
- ``contains``: materials containing every listed element (supersets).

Element symbols are case-sensitive throughout. Invalid input raises
``SearchQueryError`` with an explanation; it is never reread as something
else. The composition index is built read-only and cached per process; it
writes nothing to the database.
"""

from __future__ import annotations

import math
import re
import threading
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.periodic_table import ELEMENT_SYMBOLS
from app.models.dataset_import import DatasetImportRun, MaterialSourceRecord
from app.models.material import Material
from app.utils.chemical_formula import parse_formula_elements_strict

TAU = 1e-6
MAX_QUERY_LENGTH = 100
MAX_LIMIT = 100
SEARCH_MODES = ("formula", "mp_id", "chemsys", "contains")
MAX_SUGGESTIONS = 10
_MP_ID = re.compile(r"^mp-\d+$")
_ADDUCT = re.compile(r"[·•∙*]|\.(?=[A-Z(\[])")


class SearchQueryError(ValueError):
    def __init__(self, code: str, mode: str, query: str, explanation: str):
        super().__init__(explanation)
        self.code = code
        self.mode = mode
        self.query = query
        self.explanation = explanation

    def detail(self) -> dict:
        return {
            "code": self.code,
            "mode": self.mode,
            "input": self.query,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class IndexedMaterial:
    material_id: int
    mp_id: str
    formula: str
    pretty_formula: str
    elements: frozenset[str]
    fractions: dict[str, float]

    def result(self) -> dict:
        return {
            "material_id": self.material_id,
            "mp_id": self.mp_id,
            "formula": self.formula,
            "pretty_formula": self.pretty_formula,
        }


@dataclass(frozen=True)
class CompositionExclusion:
    material_id: int
    mp_id: str
    reason: str


@dataclass(frozen=True)
class CompositionIndex:
    fingerprint: tuple[int, int | None]
    materials: tuple[IndexedMaterial, ...]
    exclusions: tuple[CompositionExclusion, ...]
    by_element_set: dict[frozenset[str], tuple[IndexedMaterial, ...]]


def normalise_stored_composition(raw: object) -> dict[str, float]:
    """Validate stored per-element amounts and return fractions summing to 1.

    Raises ``ValueError`` with a reason for anything that cannot be a
    composition: a missing or empty mapping, an unknown symbol, or an amount
    that is non-numeric, non-finite, zero or negative.
    """
    if not isinstance(raw, dict) or not raw:
        raise ValueError("no stored composition")

    amounts: dict[str, float] = {}
    for symbol, value in raw.items():
        if symbol not in ELEMENT_SYMBOLS:
            raise ValueError(f"unknown element symbol {symbol!r}")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"non-numeric amount for {symbol}")
        amount = float(value)
        if not math.isfinite(amount):
            raise ValueError(f"non-finite amount for {symbol}")
        if amount <= 0:
            raise ValueError(f"non-positive amount for {symbol}")
        amounts[symbol] = amount

    total = sum(amounts.values())
    return {symbol: amount / total for symbol, amount in amounts.items()}


def compositions_equal(
    first: dict[str, float],
    second: dict[str, float],
    tau: float = TAU,
) -> bool:
    return set(first) == set(second) and all(
        abs(first[symbol] - second[symbol]) <= tau for symbol in first
    )


def parse_formula_query(query: str) -> dict:
    """Parse a formula query into amounts and fractions, without correction."""
    text = query.strip()
    if not text:
        raise SearchQueryError(
            "invalid_formula", "formula", query, "Enter a chemical formula."
        )
    if _ADDUCT.search(text):
        raise SearchQueryError(
            "hydrate_notation_not_supported",
            "formula",
            query,
            "Hydrate or adduct notation (for example '·H2O' or '.H2O') is not "
            "supported. Enter a single formula; it is not combined for you.",
        )
    elements = parse_formula_elements_strict(text)
    if elements is None:
        raise SearchQueryError(
            "invalid_formula",
            "formula",
            query,
            "This is not a formula this search can read. Element symbols are "
            "case-sensitive (for example 'Co' is cobalt, 'CO' is carbon and "
            "oxygen); amounts are plain numbers after a symbol or closing "
            "parenthesis; charges, brackets and leading counts are not "
            "supported.",
        )
    # Imported on first use: loading pymatgen at startup costs every worker
    # about 1.4 s and 16 MiB, whether or not it ever searches by formula.
    from pymatgen.core import Composition

    try:
        composition = Composition(text, strict=True)
    except (ValueError, TypeError) as error:
        raise SearchQueryError(
            "invalid_formula", "formula", query,
            f"The formula could not be read: {error}",
        ) from error

    amounts = {
        str(symbol): float(amount)
        for symbol, amount in composition.get_el_amt_dict().items()
    }
    dropped = sorted(set(elements) - {s for s, a in amounts.items() if a > 0})
    if dropped:
        raise SearchQueryError(
            "zero_amount",
            "formula",
            query,
            f"Element(s) {', '.join(dropped)} have a zero amount. Remove them "
            "or give a positive amount; they are not dropped for you.",
        )

    fractions = normalise_stored_composition(amounts)
    return {
        "mode": "formula",
        "input": query,
        "elements": sorted(fractions),
        "amounts": amounts,
        "normalized_fractions": fractions,
        "reduced_formula": composition.reduced_formula,
        "mp_id": None,
    }


def parse_element_list(query: str, mode: str) -> list[str]:
    separator = r"-" if mode == "chemsys" else r"[,\s]+"
    tokens = [token.strip() for token in re.split(separator, query.strip())]
    tokens = [token for token in tokens if token]
    if not tokens:
        raise SearchQueryError(
            "invalid_element_list", mode, query, "Enter at least one element."
        )
    unknown = [token for token in tokens if token not in ELEMENT_SYMBOLS]
    if unknown:
        raise SearchQueryError(
            "unknown_element",
            mode,
            query,
            f"Not recognised as element symbol(s): {', '.join(unknown)}. "
            "Symbols are case-sensitive (for example 'Co', not 'co' or 'CO').",
        )
    if len(set(tokens)) != len(tokens):
        raise SearchQueryError(
            "duplicate_element", mode, query, "An element is listed twice."
        )
    return tokens


class CompositionIndexCache:
    """Per-process, read-only cache of normalised compositions."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._index: CompositionIndex | None = None

    def get(self, db: Session) -> CompositionIndex:
        count, max_id = db.execute(
            select(func.count(Material.id), func.max(Material.id))
        ).one()
        fingerprint = (int(count), max_id)
        with self._lock:
            if self._index is None or self._index.fingerprint != fingerprint:
                self._index = build_composition_index(db, fingerprint)
            return self._index

    def clear(self) -> None:
        with self._lock:
            self._index = None


def build_composition_index(
    db: Session,
    fingerprint: tuple[int, int | None],
) -> CompositionIndex:
    rows = db.execute(
        select(
            Material.id,
            Material.mp_id,
            Material.formula,
            Material.pretty_formula,
            Material.raw_data["composition"],
        ).order_by(Material.id)
    ).all()
    return index_from_rows(rows, fingerprint)


def index_from_rows(rows, fingerprint) -> CompositionIndex:
    materials: list[IndexedMaterial] = []
    exclusions: list[CompositionExclusion] = []
    by_element_set: dict[frozenset[str], list[IndexedMaterial]] = {}
    for material_id, mp_id, formula, pretty_formula, composition in rows:
        try:
            fractions = normalise_stored_composition(composition)
        except ValueError as error:
            exclusions.append(
                CompositionExclusion(material_id, mp_id, str(error))
            )
            continue
        item = IndexedMaterial(
            material_id=material_id,
            mp_id=mp_id,
            formula=formula,
            pretty_formula=pretty_formula,
            elements=frozenset(fractions),
            fractions=fractions,
        )
        materials.append(item)
        by_element_set.setdefault(item.elements, []).append(item)
    return CompositionIndex(
        fingerprint=fingerprint,
        materials=tuple(materials),
        exclusions=tuple(exclusions),
        by_element_set={
            key: tuple(value) for key, value in by_element_set.items()
        },
    )


_CACHE = CompositionIndexCache()


class MaterialSearchService:
    def __init__(self, db: Session, cache: CompositionIndexCache = _CACHE):
        self.db = db
        self.cache = cache

    def search(self, *, mode: str, query: str, limit: int, offset: int) -> dict:
        # Bounded before any parsing or index access (route approval condition).
        if len(query) > MAX_QUERY_LENGTH:
            raise SearchQueryError(
                "query_too_long", mode, query[:MAX_QUERY_LENGTH],
                f"Queries are limited to {MAX_QUERY_LENGTH} characters; this one "
                f"has {len(query)}.",
            )
        if not 1 <= limit <= MAX_LIMIT:
            raise SearchQueryError(
                "invalid_limit", mode, query,
                f"The page size must be between 1 and {MAX_LIMIT}.",
            )
        index = self.cache.get(self.db)
        suggestions = None

        if mode == "formula":
            interpretation = parse_formula_query(query)
            elements = frozenset(interpretation["elements"])
            same_system = index.by_element_set.get(elements, ())
            matches = [
                item for item in same_system
                if compositions_equal(
                    item.fractions, interpretation["normalized_fractions"]
                )
            ]
            if not matches and same_system:
                suggestions = {
                    "basis": "same_chemical_system",
                    "explanation": (
                        "These materials have the same elements in different "
                        "proportions. They are not matches for the formula."
                    ),
                    "results": [
                        item.result() for item in same_system[:MAX_SUGGESTIONS]
                    ],
                }
        elif mode == "mp_id":
            text = query.strip()
            if not _MP_ID.match(text):
                raise SearchQueryError(
                    "invalid_mp_id", mode, query,
                    "Materials Project IDs look like 'mp-19017'.",
                )
            interpretation = {
                "mode": mode, "input": query, "elements": None,
                "amounts": None, "normalized_fractions": None,
                "reduced_formula": None, "mp_id": text,
            }
            matches = [item for item in index.materials if item.mp_id == text]
            # Identity search does not depend on a readable composition.
            if not matches:
                row = self.db.execute(
                    select(
                        Material.id, Material.mp_id, Material.formula,
                        Material.pretty_formula,
                    ).where(Material.mp_id == text)
                ).first()
                if row is not None:
                    matches = [IndexedMaterial(
                        row[0], row[1], row[2], row[3], frozenset(), {},
                    )]
        elif mode in ("chemsys", "contains"):
            elements = parse_element_list(query, mode)
            interpretation = {
                "mode": mode, "input": query, "elements": sorted(elements),
                "amounts": None, "normalized_fractions": None,
                "reduced_formula": None, "mp_id": None,
            }
            wanted = frozenset(elements)
            if mode == "chemsys":
                matches = list(index.by_element_set.get(wanted, ()))
            else:
                matches = [
                    item for item in index.materials if wanted <= item.elements
                ]
        else:
            raise SearchQueryError(
                "invalid_mode", mode, query,
                f"Choose one of: {', '.join(SEARCH_MODES)}.",
            )

        matches.sort(key=lambda item: item.material_id)
        dataset = self._dataset(index)
        page = matches[offset: offset + limit]
        return {
            "interpretation": interpretation,
            "dataset": dataset,
            "total_matches": len(matches),
            "dataset_total": dataset["dataset_total"],
            "limit": limit,
            "offset": offset,
            "results": [item.result() for item in page],
            "suggestions": suggestions,
            "message": None if matches else self._zero_message(dataset),
        }

    def _dataset(self, index: CompositionIndex) -> dict:
        total = self.db.execute(select(func.count(Material.id))).scalar_one()
        release = self.db.execute(
            select(DatasetImportRun.source_release)
            .where(DatasetImportRun.status.in_(
                ("completed", "completed_with_conflicts")
            ))
            .order_by(DatasetImportRun.completed_at.desc())
            .limit(1)
        ).scalar_one_or_none()
        with_provenance = self.db.execute(
            select(func.count(func.distinct(MaterialSourceRecord.material_id)))
            .where(MaterialSourceRecord.active.is_(True))
        ).scalar_one()
        without = total - with_provenance
        note = (
            f"{with_provenance} record{'s' if with_provenance != 1 else ''} "
            "carry release provenance; "
            f"{without} curated record{'s' if without != 1 else ''} predate "
            "provenance tracking."
        )
        return {
            "source": "materials_project",
            "source_release": release,
            "dataset_total": total,
            "provenance_note": note,
            "composition_exclusions": [
                {"material_id": e.material_id, "mp_id": e.mp_id,
                 "reason": e.reason}
                for e in index.exclusions[:20]
            ],
            "composition_exclusion_count": len(index.exclusions),
        }

    @staticmethod
    def _zero_message(dataset: dict) -> str:
        release = (
            f"Materials Project release {dataset['source_release']}"
            if dataset["source_release"]
            else "Materials Project (release not recorded in this database)"
        )
        return (
            f"No match in this dataset ({release}, "
            f"{dataset['dataset_total']} materials). The material is not in "
            "this dataset; this does not mean it does not exist."
        )
