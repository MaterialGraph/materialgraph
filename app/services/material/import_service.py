from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.services.material.project_service import MaterialCandidate
from app.services.material.composition_service import (
    MaterialCompositionService,
)


@dataclass(frozen=True)
class MaterialImportResult:
    processed: int
    imported: int
    skipped: int


class MaterialImportService:
    def __init__(self, db: Session):
        self.db = db

    def import_materials(
        self,
        candidates: list[MaterialCandidate],
    ) -> int:
        """Import one atomic batch using the session transaction.

        This service owns the transaction: it commits the complete batch on
        success and rolls back all pending session changes on failure. Callers
        must therefore provide a session dedicated to the import operation.
        """
        return self.import_materials_with_result(candidates).imported

    def import_materials_with_result(
        self,
        candidates: list[MaterialCandidate],
    ) -> MaterialImportResult:
        """Import one atomic batch and report reconciled batch counts."""
        unique_candidates: list[MaterialCandidate] = []
        duplicate_count = 0
        seen_mp_ids: set[str] = set()

        for candidate in candidates:
            if candidate.mp_id in seen_mp_ids:
                duplicate_count += 1
                continue
            seen_mp_ids.add(candidate.mp_id)
            unique_candidates.append(candidate)

        fractions_by_mp_id = {
            candidate.mp_id: MaterialCompositionService.resolve_import_fractions(
                elements=candidate.elements,
                composition_fractions=candidate.composition_fractions,
            )
            for candidate in unique_candidates
        }

        try:
            existing_mp_ids = self._find_existing_mp_ids(seen_mp_ids)
            pending_candidates = [
                candidate
                for candidate in unique_candidates
                if candidate.mp_id not in existing_mp_ids
            ]
            element_symbols = {
                symbol
                for candidate in pending_candidates
                for symbol in fractions_by_mp_id[candidate.mp_id]
            }
            elements_by_symbol = self._get_or_create_elements(element_symbols)

            for candidate in pending_candidates:
                fractions = fractions_by_mp_id[candidate.mp_id]
                fraction_known = bool(candidate.composition_fractions)

                material = self._create_material(candidate)
                self.db.flush()

                self._link_elements(
                    material_id=material.id,
                    fractions=fractions,
                    fraction_known=fraction_known,
                    elements_by_symbol=elements_by_symbol,
                )

            self.db.commit()

            imported_count = len(pending_candidates)
            skipped_count = len(existing_mp_ids) + duplicate_count

            return MaterialImportResult(
                processed=len(candidates),
                imported=imported_count,
                skipped=skipped_count,
            )
        except Exception:
            self.db.rollback()
            raise

    def _find_existing_mp_ids(self, mp_ids: set[str]) -> set[str]:
        if not mp_ids:
            return set()

        return {
            row[0]
            for row in self.db.query(Material.mp_id)
            .filter(Material.mp_id.in_(mp_ids))
            .all()
        }

    def count_existing_materials(self, mp_ids: set[str]) -> int:
        """Count manifest identities present after an import application."""
        return len(self._find_existing_mp_ids(mp_ids))

    def _get_or_create_elements(
        self,
        symbols: set[str],
    ) -> dict[str, Element]:
        if not symbols:
            return {}

        existing = (
            self.db.query(Element)
            .filter(Element.symbol.in_(symbols))
            .all()
        )
        elements_by_symbol = {
            element.symbol: element
            for element in existing
        }

        for symbol in sorted(symbols - elements_by_symbol.keys()):
            element = Element(symbol=symbol, name=symbol)
            self.db.add(element)
            elements_by_symbol[symbol] = element

        self.db.flush()

        return elements_by_symbol

    def _material_exists(self, mp_id: str) -> bool:
        """Compatibility helper for callers that check one source identity."""
        return mp_id in self._find_existing_mp_ids({mp_id})

    def _create_material(
        self,
        candidate: MaterialCandidate,
    ) -> Material:
        material = Material(
            mp_id=candidate.mp_id,
            formula=candidate.formula,
            pretty_formula=candidate.pretty_formula,
            band_gap=candidate.band_gap,
            energy_above_hull=candidate.energy_above_hull,
            formation_energy_per_atom=candidate.formation_energy_per_atom,
            density=candidate.density,
            is_stable=candidate.is_stable,
            raw_data=candidate.raw_data,
            source="materials_project",
        )

        self.db.add(material)

        return material

    def _link_elements(
        self,
        material_id: int,
        fractions: dict[str, float],
        fraction_known: bool,
        elements_by_symbol: dict[str, Element],
    ) -> None:
        for symbol, fraction in sorted(fractions.items()):
            element = elements_by_symbol[symbol]

            self.db.add(
                MaterialElement(
                    material_id=material_id,
                    element_id=element.id,
                    fraction=fraction,
                    fraction_known=fraction_known,
                )
            )
