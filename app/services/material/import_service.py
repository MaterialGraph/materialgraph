import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.element import Element
from app.models.dataset_import import (
    DatasetImportRun,
    MaterialImportEvent,
    MaterialSourceMembership,
    MaterialSourceRecord,
)
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


@dataclass(frozen=True)
class DatasetImportRunSpec:
    import_run_id: str
    source: str
    source_release: str
    retrieved_at: datetime
    manifest_sha256: str
    normalization_version: str
    selection_contract_version: str
    selection_scope_sha256: str
    license_identifier: str
    license_url: str


@dataclass(frozen=True)
class MaterialRefreshResult:
    processed: int
    inserted: int
    updated: int
    unchanged: int
    conflicted: int


@dataclass(frozen=True)
class DatasetImportCompletion:
    retired: int


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

    def begin_import_run(
        self,
        *,
        spec: DatasetImportRunSpec,
        rejections: list[dict],
    ) -> None:
        """Create an immutable run header and persist manifest rejections."""
        try:
            existing = self.db.get(DatasetImportRun, spec.import_run_id)
            if existing is None:
                self.db.add(
                    DatasetImportRun(
                        id=spec.import_run_id,
                        source=spec.source,
                        source_release=spec.source_release,
                        retrieved_at=spec.retrieved_at,
                        manifest_sha256=spec.manifest_sha256,
                        normalization_version=spec.normalization_version,
                        selection_contract_version=spec.selection_contract_version,
                        selection_scope_sha256=spec.selection_scope_sha256,
                        license_identifier=spec.license_identifier,
                        license_url=spec.license_url,
                        status="running",
                        outcome_counts=None,
                        started_at=datetime.now(timezone.utc),
                        completed_at=None,
                    )
                )
                self.db.flush()
            else:
                self._validate_existing_run(existing, spec)

            existing_keys = {
                value
                for (value,) in self.db.query(MaterialImportEvent.event_key)
                .filter(MaterialImportEvent.import_run_id == spec.import_run_id)
                .all()
            }
            for index, rejection in enumerate(rejections):
                event_key = f"reject:{index}"
                if event_key in existing_keys:
                    continue
                self.db.add(
                    MaterialImportEvent(
                        import_run_id=spec.import_run_id,
                        event_key=event_key,
                        source_id=rejection.get("source_id"),
                        material_id=None,
                        outcome="rejected",
                        source_record_sha256=None,
                        normalized_record_sha256=None,
                        reason=str(rejection["reason"]),
                        recorded_at=datetime.now(timezone.utc),
                    )
                )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def refresh_materials(
        self,
        candidates: list[MaterialCandidate],
        *,
        import_run_id: str,
    ) -> MaterialRefreshResult:
        """Apply one provenance-aware refresh chunk atomically."""
        run = self.db.get(DatasetImportRun, import_run_id)
        if run is None or run.status != "running":
            raise ValueError("import run is missing or not running")

        source_ids = [candidate.mp_id for candidate in candidates]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("refresh chunk contains duplicate source identities")

        event_keys = {f"candidate:{source_id}" for source_id in source_ids}
        existing_events = (
            self.db.query(MaterialImportEvent)
            .filter(
                MaterialImportEvent.import_run_id == import_run_id,
                MaterialImportEvent.event_key.in_(event_keys),
            )
            .all()
        )
        if existing_events:
            if len(existing_events) != len(candidates):
                raise ValueError("import run contains a partial chunk outcome")
            counts = {
                outcome: sum(event.outcome == outcome for event in existing_events)
                for outcome in ("inserted", "updated", "unchanged", "conflicted")
            }
            return MaterialRefreshResult(
                processed=len(candidates),
                inserted=counts["inserted"],
                updated=counts["updated"],
                unchanged=counts["unchanged"],
                conflicted=counts["conflicted"],
            )

        fractions_by_source_id = {
            candidate.mp_id: MaterialCompositionService.resolve_import_fractions(
                elements=candidate.elements,
                composition_fractions=candidate.composition_fractions,
            )
            for candidate in candidates
        }
        records_by_source_id = {
            record.source_id: record
            for record in self.db.query(MaterialSourceRecord)
            .filter(
                MaterialSourceRecord.source == run.source,
                MaterialSourceRecord.source_id.in_(source_ids),
            )
            .all()
        }
        record_ids = {record.id for record in records_by_source_id.values()}
        memberships_by_record_id = {
            membership.source_record_id: membership
            for membership in self.db.query(MaterialSourceMembership)
            .filter(
                MaterialSourceMembership.source_record_id.in_(record_ids),
                MaterialSourceMembership.selection_contract_version
                == run.selection_contract_version,
                MaterialSourceMembership.selection_scope_sha256
                == run.selection_scope_sha256,
            )
            .all()
        }
        materials_by_mp_id = {
            material.mp_id: material
            for material in self.db.query(Material)
            .filter(Material.mp_id.in_(source_ids))
            .all()
        }
        inserted = updated = unchanged = conflicted = 0

        try:
            for candidate in candidates:
                source_digest = self._digest(candidate.raw_data)
                normalized_digest = self._normalized_candidate_digest(
                    candidate,
                    fractions_by_source_id[candidate.mp_id],
                )
                record = records_by_source_id.get(candidate.mp_id)
                material = materials_by_mp_id.get(candidate.mp_id)

                if record is None and material is not None:
                    conflicted += 1
                    self._add_event(
                        run=run,
                        candidate=candidate,
                        material=material,
                        outcome="conflicted",
                        source_digest=source_digest,
                        normalized_digest=normalized_digest,
                        reason="source identity already exists without matching provenance",
                    )
                    continue

                if record is None:
                    material = self._create_material(
                        candidate,
                        source=run.source,
                    )
                    self.db.flush()
                    self._replace_element_links(
                        material=material,
                        candidate=candidate,
                        fractions=fractions_by_source_id[candidate.mp_id],
                    )
                    record = MaterialSourceRecord(
                        material_id=material.id,
                        source=run.source,
                        source_id=candidate.mp_id,
                        source_release=run.source_release,
                        source_record_sha256=source_digest,
                        normalized_record_sha256=normalized_digest,
                        normalization_version=run.normalization_version,
                        selection_contract_version=run.selection_contract_version,
                        selection_scope_sha256=run.selection_scope_sha256,
                        retrieved_at=run.retrieved_at,
                        latest_import_run_id=run.id,
                        active=True,
                    )
                    self.db.add(record)
                    self.db.flush()
                    inserted += 1
                    outcome = "inserted"
                elif record.material_id != (material.id if material else None):
                    conflicted += 1
                    self._add_event(
                        run=run,
                        candidate=candidate,
                        material=material,
                        outcome="conflicted",
                        source_digest=source_digest,
                        normalized_digest=normalized_digest,
                        reason="source identity does not resolve to its recorded material",
                    )
                    continue
                elif (
                    record.source_record_sha256 == source_digest
                    and record.normalized_record_sha256 == normalized_digest
                    and record.normalization_version == run.normalization_version
                ):
                    unchanged += 1
                    outcome = "unchanged"
                else:
                    self._update_material(material, candidate)
                    self._replace_element_links(
                        material=material,
                        candidate=candidate,
                        fractions=fractions_by_source_id[candidate.mp_id],
                    )
                    updated += 1
                    outcome = "updated"

                record.source_release = run.source_release
                record.source_record_sha256 = source_digest
                record.normalized_record_sha256 = normalized_digest
                record.normalization_version = run.normalization_version
                record.selection_contract_version = run.selection_contract_version
                record.selection_scope_sha256 = run.selection_scope_sha256
                record.retrieved_at = run.retrieved_at
                record.latest_import_run_id = run.id
                record.active = True
                membership = memberships_by_record_id.get(record.id)
                if membership is None:
                    membership = MaterialSourceMembership(
                        source_record_id=record.id,
                        selection_contract_version=run.selection_contract_version,
                        selection_scope_sha256=run.selection_scope_sha256,
                        latest_import_run_id=run.id,
                        active=True,
                    )
                    self.db.add(membership)
                    memberships_by_record_id[record.id] = membership
                else:
                    membership.latest_import_run_id = run.id
                    membership.active = True
                self._add_event(
                    run=run,
                    candidate=candidate,
                    material=material,
                    outcome=outcome,
                    source_digest=source_digest,
                    normalized_digest=normalized_digest,
                )

            self.db.commit()
            return MaterialRefreshResult(
                processed=len(candidates),
                inserted=inserted,
                updated=updated,
                unchanged=unchanged,
                conflicted=conflicted,
            )
        except Exception:
            self.db.rollback()
            raise

    def complete_import_run(
        self,
        *,
        import_run_id: str,
        manifest_source_ids: set[str],
        outcome_counts: dict[str, int],
        allow_retirement: bool,
    ) -> DatasetImportCompletion:
        """Retire absent records in the identical source selection scope."""
        run = self.db.get(DatasetImportRun, import_run_id)
        completed_statuses = {"completed", "completed_with_conflicts"}
        if run is None or run.status not in {"running", *completed_statuses}:
            raise ValueError("import run is missing or invalid")
        if run.status in completed_statuses:
            return DatasetImportCompletion(retired=run.outcome_counts["retired"])

        try:
            observed_counts = {
                outcome: (
                    self.db.query(MaterialImportEvent)
                    .filter(
                        MaterialImportEvent.import_run_id == run.id,
                        MaterialImportEvent.outcome == outcome,
                    )
                    .count()
                )
                for outcome in (
                    "inserted",
                    "updated",
                    "unchanged",
                    "conflicted",
                    "rejected",
                )
            }
            if outcome_counts != observed_counts:
                raise ValueError("import run outcome counts do not reconcile")

            query = (
                self.db.query(MaterialSourceMembership, MaterialSourceRecord)
                .join(
                    MaterialSourceRecord,
                    MaterialSourceMembership.source_record_id
                    == MaterialSourceRecord.id,
                )
                .filter(
                    MaterialSourceRecord.source == run.source,
                    MaterialSourceMembership.selection_contract_version
                    == run.selection_contract_version,
                    MaterialSourceMembership.selection_scope_sha256
                    == run.selection_scope_sha256,
                    MaterialSourceMembership.active.is_(True),
                )
            )
            if not allow_retirement:
                query = query.filter(False)
            if manifest_source_ids:
                query = query.filter(
                    MaterialSourceRecord.source_id.notin_(manifest_source_ids)
                )
            retired_memberships = query.all()
            for membership, record in retired_memberships:
                membership.active = False
                membership.latest_import_run_id = run.id
                self.db.add(
                    MaterialImportEvent(
                        import_run_id=run.id,
                        event_key=f"retired:{record.source_id}",
                        source_id=record.source_id,
                        material_id=record.material_id,
                        outcome="retired",
                        source_record_sha256=record.source_record_sha256,
                        normalized_record_sha256=record.normalized_record_sha256,
                        reason="absent from the completed identical selection scope",
                        recorded_at=datetime.now(timezone.utc),
                    )
                )

            self.db.flush()
            for _, record in retired_memberships:
                record.active = (
                    self.db.query(MaterialSourceMembership)
                    .filter(
                        MaterialSourceMembership.source_record_id == record.id,
                        MaterialSourceMembership.active.is_(True),
                    )
                    .count()
                    > 0
                )

            completed_counts = dict(outcome_counts)
            completed_counts["retired"] = len(retired_memberships)
            run.status = (
                "completed_with_conflicts"
                if completed_counts["conflicted"]
                else "completed"
            )
            run.outcome_counts = completed_counts
            run.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            return DatasetImportCompletion(retired=len(retired_memberships))
        except Exception:
            self.db.rollback()
            raise

    @staticmethod
    def _validate_existing_run(
        run: DatasetImportRun,
        spec: DatasetImportRunSpec,
    ) -> None:
        expected = {
            "source": spec.source,
            "source_release": spec.source_release,
            "retrieved_at": spec.retrieved_at,
            "manifest_sha256": spec.manifest_sha256,
            "normalization_version": spec.normalization_version,
            "selection_contract_version": spec.selection_contract_version,
            "selection_scope_sha256": spec.selection_scope_sha256,
            "license_identifier": spec.license_identifier,
            "license_url": spec.license_url,
        }
        if any(getattr(run, key) != value for key, value in expected.items()):
            raise ValueError("import run identity does not match manifest provenance")

    def _add_event(
        self,
        *,
        run: DatasetImportRun,
        candidate: MaterialCandidate,
        material: Material | None,
        outcome: str,
        source_digest: str,
        normalized_digest: str,
        reason: str | None = None,
    ) -> None:
        self.db.add(
            MaterialImportEvent(
                import_run_id=run.id,
                event_key=f"candidate:{candidate.mp_id}",
                source_id=candidate.mp_id,
                material_id=material.id if material else None,
                outcome=outcome,
                source_record_sha256=source_digest,
                normalized_record_sha256=normalized_digest,
                reason=reason,
                recorded_at=datetime.now(timezone.utc),
            )
        )

    @staticmethod
    def _digest(value: dict) -> str:
        canonical = json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @classmethod
    def _normalized_candidate_digest(
        cls,
        candidate: MaterialCandidate,
        fractions: dict[str, float],
    ) -> str:
        return cls._digest(
            {
                "band_gap": candidate.band_gap,
                "composition_fractions": fractions,
                "density": candidate.density,
                "elements": sorted(fractions),
                "energy_above_hull": candidate.energy_above_hull,
                "formation_energy_per_atom": candidate.formation_energy_per_atom,
                "formula": candidate.formula,
                "is_stable": candidate.is_stable,
                "mp_id": candidate.mp_id,
                "pretty_formula": candidate.pretty_formula,
            }
        )

    def _update_material(
        self,
        material: Material,
        candidate: MaterialCandidate,
    ) -> None:
        material.formula = candidate.formula
        material.pretty_formula = candidate.pretty_formula
        material.band_gap = candidate.band_gap
        material.energy_above_hull = candidate.energy_above_hull
        material.formation_energy_per_atom = candidate.formation_energy_per_atom
        material.density = candidate.density
        material.is_stable = candidate.is_stable
        material.raw_data = candidate.raw_data

    def _replace_element_links(
        self,
        *,
        material: Material,
        candidate: MaterialCandidate,
        fractions: dict[str, float],
    ) -> None:
        self.db.query(MaterialElement).filter(
            MaterialElement.material_id == material.id
        ).delete(synchronize_session=False)
        elements_by_symbol = self._get_or_create_elements(set(fractions))
        self._link_elements(
            material_id=material.id,
            fractions=fractions,
            fraction_known=bool(candidate.composition_fractions),
            elements_by_symbol=elements_by_symbol,
        )

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

    def count_active_source_records(
        self,
        *,
        source: str,
        source_ids: set[str],
        selection_contract_version: str,
        selection_scope_sha256: str,
    ) -> int:
        if not source_ids:
            return 0
        return (
            self.db.query(MaterialSourceMembership)
            .join(
                MaterialSourceRecord,
                MaterialSourceMembership.source_record_id
                == MaterialSourceRecord.id,
            )
            .filter(
                MaterialSourceRecord.source == source,
                MaterialSourceRecord.source_id.in_(source_ids),
                MaterialSourceMembership.selection_contract_version
                == selection_contract_version,
                MaterialSourceMembership.selection_scope_sha256
                == selection_scope_sha256,
                MaterialSourceMembership.active.is_(True),
            )
            .count()
        )

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
        *,
        source: str = "materials_project",
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
            source=source,
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
