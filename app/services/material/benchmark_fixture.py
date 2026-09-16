from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.services.material.import_pipeline import (
    SYNTHETIC_BENCHMARK_LICENSE,
    SYNTHETIC_BENCHMARK_LICENSE_URL,
    SYNTHETIC_BENCHMARK_SOURCE,
    ManifestBuildResult,
    MaterialDatasetContract,
    MaterialImportPipeline,
    MaterialImportScope,
)
from app.services.material.project_service import (
    MaterialCandidate,
    MaterialCandidateRejection,
    MaterialFetchPage,
)


FIXTURE_SCHEMA_VERSION = 1
FIXTURE_SEED = 20260916
FIXTURE_SOURCE_RELEASE = "mg-de-004-synthetic-v1"
FIXTURE_RETRIEVED_AT = "2026-09-16T00:00:00+00:00"
FIXTURE_NORMALIZATION_VERSION = "mg-de-004-synthetic-normalization-v1"
FIXTURE_SELECTION_VERSION = "mg-de-004-representative-selection-v1"
FIXTURE_ID_PREFIX = "mgde004-"
FIXTURE_CHEMICAL_SYSTEMS = (
    "Fe-O",
    "Fe-O-P",
    "Li-Fe-O-P",
    "Na-Mn-O",
    "Si-O",
)


@dataclass(frozen=True)
class _FixtureEntry:
    candidate: MaterialCandidate | None = None
    rejection: MaterialCandidateRejection | None = None


class SyntheticBenchmarkSource:
    """Deterministic, offline source for bounded scale qualification only."""

    def __init__(self, *, unique_materials: int):
        if not 1 <= unique_materials <= 10_000:
            raise ValueError("unique_materials must be between 1 and 10000")
        self._streams = {
            chemical_system: []
            for chemical_system in FIXTURE_CHEMICAL_SYSTEMS
        }
        for ordinal in range(unique_materials):
            system = FIXTURE_CHEMICAL_SYSTEMS[
                ordinal % len(FIXTURE_CHEMICAL_SYSTEMS)
            ]
            self._streams[system].append(
                _FixtureEntry(candidate=self._candidate(ordinal))
            )

        for index, system in enumerate(FIXTURE_CHEMICAL_SYSTEMS):
            stream = self._streams[system]
            if not stream:
                continue
            duplicate = stream[min(25, len(stream) - 1)].candidate
            stream.insert(40, _FixtureEntry(candidate=duplicate))
            stream.insert(
                80,
                _FixtureEntry(
                    rejection=MaterialCandidateRejection(
                        source_id=f"{FIXTURE_ID_PREFIX}invalid-{index}",
                        reason="synthetic_controlled_rejection",
                    )
                ),
            )

    def fetch_materials_page(
        self,
        *,
        chemsys: str,
        page: int,
        page_size: int,
        stable_only: bool,
    ) -> MaterialFetchPage:
        if chemsys not in self._streams:
            raise ValueError("unknown synthetic fixture chemical system")
        if page < 1:
            raise ValueError("page must be at least 1")
        start = (page - 1) * page_size
        entries = self._streams[chemsys][start : start + page_size]
        candidates = [
            entry.candidate
            for entry in entries
            if entry.candidate is not None
            and (entry.candidate.is_stable or not stable_only)
        ]
        rejections = [
            entry.rejection
            for entry in entries
            if entry.rejection is not None
        ]
        return MaterialFetchPage(
            candidates=candidates,
            rejections=rejections,
        )

    @staticmethod
    def _candidate(ordinal: int) -> MaterialCandidate:
        cohort, elements, formula = _fixture_identity(ordinal)
        fraction = 1.0 / len(elements)
        energy_above_hull = (
            None if ordinal % 17 == 0 else round((ordinal % 21) / 100.0, 3)
        )
        is_stable = (
            energy_above_hull == 0.0
            if energy_above_hull is not None
            else False
        )
        return MaterialCandidate(
            mp_id=f"{FIXTURE_ID_PREFIX}{ordinal:05d}",
            formula=formula,
            pretty_formula=formula,
            elements=elements,
            band_gap=None if ordinal % 11 == 0 else round((ordinal % 40) / 10, 3),
            energy_above_hull=energy_above_hull,
            formation_energy_per_atom=(
                None if ordinal % 13 == 0 else round(-0.1 - (ordinal % 30) / 10, 3)
            ),
            density=None if ordinal % 19 == 0 else round(1.0 + (ordinal % 80) / 10, 3),
            is_stable=is_stable,
            raw_data={
                "benchmark_fixture": True,
                "cohort": cohort,
                "fixture_schema_version": FIXTURE_SCHEMA_VERSION,
                "fixture_seed": FIXTURE_SEED,
                "ordinal": ordinal,
                "synthetic": True,
            },
            composition_fractions={symbol: fraction for symbol in elements},
        )


def _fixture_identity(ordinal: int) -> tuple[str, list[str], str]:
    if ordinal < 400:
        modifiers = (
            "Li",
            "Na",
            "K",
            "Mn",
            "Co",
            "Ni",
            "Ti",
            "V",
            "Cr",
            "Mg",
        )
        modifier = modifiers[ordinal % len(modifiers)]
        elements = sorted({"Fe", "P", "O", modifier})
        return "dense_phosphate", elements, f"{modifier}FePO4"
    if ordinal < 700:
        transition = ("Fe", "Mn", "Co", "Ni", "Ti", "V", "Cr")[ordinal % 7]
        modifier = ("Li", "Na", "Mg", "Al", "Si")[ordinal % 5]
        elements = sorted({"O", transition, modifier})
        return "dense_oxide", elements, f"{modifier}{transition}O2"
    if ordinal < 880:
        sparse = ("B", "C", "N", "F", "Si", "S", "Cl", "Ca", "Zn", "Cu")
        first = sparse[ordinal % len(sparse)]
        second = sparse[(ordinal * 3 + 1) % len(sparse)]
        elements = sorted({first, second})
        return "sparse", elements, "".join(elements)
    if ordinal < 980:
        group = (ordinal - 880) // 5
        elements = ["O", "Ti"]
        return "polymorph", elements, f"TiO2-P{group:02d}"

    modifier = ("Al", "B", "C", "N", "S")[ordinal % 5]
    elements = sorted({"Si", "O", modifier})
    return "missing_optional", elements, f"{modifier}SiO2"


def build_representative_fixture_manifest(
    *,
    manifest_path: Path,
    target_materials: int = 1_000,
    chunk_size: int = 100,
) -> ManifestBuildResult:
    if manifest_path.exists():
        raise ValueError("refusing to overwrite an existing fixture manifest")
    source = SyntheticBenchmarkSource(
        unique_materials=target_materials,
    )
    return MaterialImportPipeline(source).build_manifest(
        scope=MaterialImportScope(
            chemical_systems=FIXTURE_CHEMICAL_SYSTEMS,
            page_size=100,
            chunk_size=chunk_size,
            max_materials=min(10_000, target_materials + 100),
            max_source_records=target_materials + 200,
            max_pages_per_system=5,
            max_fetch_attempts=1,
            stable_only=False,
        ),
        dataset=MaterialDatasetContract(
            source=SYNTHETIC_BENCHMARK_SOURCE,
            source_release=FIXTURE_SOURCE_RELEASE,
            retrieved_at=FIXTURE_RETRIEVED_AT,
            normalization_version=FIXTURE_NORMALIZATION_VERSION,
            selection_contract_version=FIXTURE_SELECTION_VERSION,
            license_identifier=SYNTHETIC_BENCHMARK_LICENSE,
            license_url=SYNTHETIC_BENCHMARK_LICENSE_URL,
        ),
        manifest_path=manifest_path,
    )
