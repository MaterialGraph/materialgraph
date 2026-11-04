import time
from collections import deque
from collections.abc import Collection

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain import ordering
from app.domain.ordering import mp_id_sort_key
from app.domain.relationship_labels import relationship_text
from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.services.discovery.candidate_service import DiscoveryCandidateService
from app.services.discovery.transition_validator import DiscoveryTransitionValidator
from app.services.material.family_service import MaterialFamilyService
from app.services.material.formula_correspondence import classify_formula_correspondence
from app.services.material.search_service import (
    compositions_equal,
    normalise_stored_composition,
)


class DiscoveryChainService:
    DEFAULT_MAX_HOPS = 2
    MAX_ALLOWED_HOPS = 3
    DEFAULT_LIMIT = 5
    EXPANSION_LIMIT = 6
    SEARCH_STATE_BUDGET = 200

    def __init__(self, db: Session):
        self.db = db
        self.candidate_service = DiscoveryCandidateService(db)
        self.family_service = MaterialFamilyService(db)
        self.transition_validator = DiscoveryTransitionValidator()
        self._candidate_cache: dict[
            tuple[int, tuple[str, ...], tuple[str, ...], bool, bool, bool],
            list[dict],
        ] = {}
        self._relationship_cache: dict[tuple[int, int], list[str]] = {}
        self._admission_diagnostics: dict[
            tuple[int, tuple[str, ...], tuple[str, ...], bool, bool, bool],
            dict[str, int],
        ] = {}
        self._family_result_cache: dict[int, dict] = {}

    def get_discovery_chains(
        self,
        material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_hops: int = DEFAULT_MAX_HOPS,
        limit: int = DEFAULT_LIMIT,
        avoid_elements: Collection[str] | None = None,
        prefer_elements: Collection[str] | None = None,
        include_search_pool: bool = False,
        hard_avoid_admission: bool = False,
        objective_aware_prefer_allocation: bool = False,
        reject_introduced_avoided: bool = True,
        objective_aware_ordering: bool = False,
    ) -> dict:
        max_hops = min(max_hops, self.MAX_ALLOWED_HOPS)

        normalized_avoid_elements = self._normalize_elements(
            element=avoid_element,
            elements=avoid_elements,
        )
        normalized_prefer_elements = self._normalize_elements(
            element=prefer_element,
            elements=prefer_elements,
        )

        base_material = self.db.get(Material, material_id)

        if base_material is None:
            return self._empty_response(
                material_id=material_id,
                avoid_element=avoid_element,
                prefer_element=prefer_element,
                max_hops=max_hops,
                limit=limit,
            )

        elements_map = self._get_material_elements_map()
        chain_pool, search_metadata = self._build_chains(
            base_material=base_material,
            elements_map=elements_map,
            avoid_elements=normalized_avoid_elements,
            prefer_elements=normalized_prefer_elements,
            max_hops=max_hops,
            hard_avoid_admission=hard_avoid_admission,
            objective_aware_prefer_allocation=objective_aware_prefer_allocation,
            reject_introduced_avoided=reject_introduced_avoided,
            objective_aware_ordering=objective_aware_ordering,
        )
        chains = chain_pool if include_search_pool else chain_pool[:limit]
        search_metadata = {
            **search_metadata,
            "requested_result_limit": limit,
            "returned_chain_count": len(chains),
            "result_truncated": len(chain_pool) > limit,
        }

        return {
            "material_id": base_material.id,
            "mp_id": base_material.mp_id,
            "base_formula": (
                base_material.pretty_formula
                or base_material.formula
            ),
            "discovery_goal": {
                "avoid_element": avoid_element,
                "prefer_element": prefer_element,
                "max_hops": max_hops,
                "limit": limit,
            },
            "search_metadata": search_metadata,
            "chains": chains,
        }

    def _build_chains(
        self,
        base_material: Material,
        elements_map: dict[int, list[str]],
        avoid_elements: frozenset[str],
        prefer_elements: frozenset[str],
        max_hops: int,
        hard_avoid_admission: bool = False,
        objective_aware_prefer_allocation: bool = False,
        reject_introduced_avoided: bool = True,
        objective_aware_ordering: bool = False,
    ) -> tuple[list[dict], dict]:
        queue = deque()

        base_node = self._material_to_node(base_material)

        queue.append({
            "materials": [base_node],
            "transitions": [],
            "visited_ids": {base_material.id},
        })

        completed_chains = []

        expanded_state_count = 0
        # Per-expansion admission counts (#51). Recording is additive: it
        # never changes which candidates are admitted.
        admission_totals = {
            "considered": 0,
            "eligible": 0,
            "admitted": 0,
            "cap_discarded": 0,
        }
        expansions_with_cap_discards = 0
        distinct_cap_discarded_ids: set[int] = set()

        while queue and expanded_state_count < self.SEARCH_STATE_BUDGET:
            current_chain = queue.popleft()
            expanded_state_count += 1
            current_material = current_chain["materials"][-1]
            current_hops = len(current_chain["transitions"])

            if current_hops >= max_hops:
                completed_chains.append(
                    self._finalize_chain(current_chain)
                )
                continue

            candidate_start = time.perf_counter()
            self.__dict__["_last_admission_key"] = None
            next_candidates = self._get_next_candidates(
                material_id=current_material["material_id"],
                avoid_elements=avoid_elements,
                prefer_elements=prefer_elements,
                elements_map=elements_map,
                hard_avoid_admission=hard_avoid_admission,
                objective_aware_prefer_allocation=objective_aware_prefer_allocation,
                objective_aware_ordering=objective_aware_ordering,
                reject_introduced_avoided=reject_introduced_avoided,
            )
            logger.info(
                "Next candidates for material {} took {:.3f}s count={}",
                current_material["material_id"],
                time.perf_counter() - candidate_start,
                len(next_candidates),
            )
            counts = self._last_admission_counts()
            for key in admission_totals:
                admission_totals[key] += counts[key]
            if counts["cap_discarded"]:
                expansions_with_cap_discards += 1
                distinct_cap_discarded_ids.update(
                    counts["cap_discarded_ids"]
                )

            for candidate in next_candidates:
                candidate_id = candidate["material_id"]

                if candidate_id in current_chain["visited_ids"]:
                    continue

                transition_start = time.perf_counter()
                transition = self._build_transition(
                    from_material=current_material,
                    to_candidate=candidate,
                    elements_map=elements_map,
                    avoid_elements=avoid_elements,
                    prefer_elements=prefer_elements,
                    reject_introduced_avoided=reject_introduced_avoided,
                )
                logger.info(
                    "Transition {} -> {} took {:.3f}s",
                    current_material["material_id"],
                    candidate_id,
                    time.perf_counter() - transition_start,
                )

                if transition is None:
                    continue

                next_chain = {
                    "materials": [
                        *current_chain["materials"],
                        self._candidate_to_node(candidate),
                    ],
                    "transitions": [
                        *current_chain["transitions"],
                        transition,
                    ],
                    "visited_ids": {
                        *current_chain["visited_ids"],
                        candidate_id,
                    },
                }

                completed_chains.append(
                    self._finalize_chain(next_chain)
                )

                if len(next_chain["transitions"]) < max_hops:
                    queue.append(next_chain)

        return completed_chains, {
            "search_policy": "bounded_breadth_first",
            "requested_result_limit": 0,
            "expansion_limit_per_material": self.EXPANSION_LIMIT,
            "search_state_budget": self.SEARCH_STATE_BUDGET,
            "expanded_state_count": expanded_state_count,
            "generated_chain_count": len(completed_chains),
            "returned_chain_count": 0,
            "search_truncated": bool(queue),
            "result_truncated": False,
            "scientific_completeness_guaranteed": False,
            "expansion_limit_binding": admission_totals["cap_discarded"] > 0,
            "expansions_with_cap_discards": expansions_with_cap_discards,
            "candidates_considered_total": admission_totals["considered"],
            "candidates_eligible_total": admission_totals["eligible"],
            "candidates_admitted_total": admission_totals["admitted"],
            "candidates_discarded_by_expansion_limit_total": (
                admission_totals["cap_discarded"]
            ),
            "distinct_candidates_discarded_by_expansion_limit": len(
                distinct_cap_discarded_ids
            ),
        }

    def _admission_counts_store(self) -> dict:
        # Created lazily so services built without __init__ (as some tests
        # do) still record counts.
        return self.__dict__.setdefault("_admission_counts", {})

    def _record_admission_counts(
        self,
        cache_key: tuple,
        *,
        considered: int,
        eligible: list[dict],
        admitted: list[dict],
    ) -> None:
        admitted_ids = {candidate["material_id"] for candidate in admitted}
        cap_discarded_ids = [
            candidate["material_id"]
            for candidate in eligible
            if candidate["material_id"] not in admitted_ids
        ]
        self._admission_counts_store()[cache_key] = {
            "considered": considered,
            "eligible": len(eligible),
            "admitted": len(admitted),
            "cap_discarded": len(cap_discarded_ids),
            "cap_discarded_ids": cap_discarded_ids,
        }
        self.__dict__["_last_admission_key"] = cache_key

    def _last_admission_counts(self) -> dict:
        key = self.__dict__.get("_last_admission_key")
        return self._admission_counts_store().get(key) or {
            "considered": 0,
            "eligible": 0,
            "admitted": 0,
            "cap_discarded": 0,
            "cap_discarded_ids": [],
        }

    def _get_next_candidates(
        self,
        material_id: int,
        elements_map: dict[int, list[str]],
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        avoid_elements: Collection[str] | None = None,
        prefer_elements: Collection[str] | None = None,
        hard_avoid_admission: bool = False,
        objective_aware_prefer_allocation: bool = False,
        objective_aware_ordering: bool = False,
        reject_introduced_avoided: bool = True,
    ) -> list[dict]:
        normalized_avoid_elements = self._normalize_elements(
            element=avoid_element,
            elements=avoid_elements,
        )
        normalized_prefer_elements = self._normalize_elements(
            element=prefer_element,
            elements=prefer_elements,
        )

        cache_key = (
            material_id,
            tuple(sorted(normalized_avoid_elements)),
            tuple(sorted(normalized_prefer_elements)),
            hard_avoid_admission,
            objective_aware_prefer_allocation,
            objective_aware_ordering,
            reject_introduced_avoided,
        )

        if cache_key in self._candidate_cache:
            self.__dict__["_last_admission_key"] = cache_key
            return self._candidate_cache[cache_key]

        family_result = self._get_family_result(material_id)
        candidates = []
        non_test_candidates = [
            candidate
            for candidate in family_result["related_materials"]
            if not (candidate.get("mp_id") or "").startswith("mp-test")
        ]

        # Preserve the legacy bounded admission path for existing callers.
        if not hard_avoid_admission and (
            not objective_aware_prefer_allocation
            or not normalized_prefer_elements
        ):
            for candidate in family_result["related_materials"]:
                mp_id = candidate.get("mp_id") or ""

                if mp_id.startswith("mp-test"):
                    continue

                candidates.append(candidate)

                if len(candidates) >= self.EXPANSION_LIMIT:
                    break

            self._record_admission_counts(
                cache_key,
                considered=len(non_test_candidates),
                eligible=non_test_candidates,
                admitted=candidates,
            )
            self._candidate_cache[cache_key] = candidates
            return candidates

        eligible_candidates = []
        missing_membership_excluded = 0
        # Finding 1 (approved refinement): Strict hard Avoid fails closed.
        # A candidate without MaterialElement membership cannot be shown to
        # be free of avoided elements, so it must not consume admission
        # capacity. Applies only when there is something to avoid.
        fail_closed_unknown_composition = hard_avoid_admission and bool(
            normalized_avoid_elements
        )

        for candidate in family_result["related_materials"]:
            mp_id = candidate.get("mp_id") or ""

            if mp_id.startswith("mp-test"):
                continue

            candidate_elements = set(
                elements_map.get(candidate["material_id"], [])
            )

            if fail_closed_unknown_composition and not candidate_elements:
                missing_membership_excluded += 1
                continue

            if (
                hard_avoid_admission
                and candidate_elements.intersection(normalized_avoid_elements)
            ):
                continue

            eligible_candidates.append(candidate)

        if objective_aware_ordering:
            # SRQ-01 R5a: on objective-aware requests, ties in the family
            # order fall to the numeric MP ID instead of the local ID.
            # Reservation and fill below walk this order, and the admitted
            # list keeps it.
            eligible_candidates.sort(key=self._admission_order_key)
            # SRQ-01 R3: exact alkali formula analogs of the expanding material
            # that share a normalised composition use one admission slot;
            # only the group's representative stays eligible.
            eligible_candidates = self._group_exact_analogs(
                cache_key,
                material_id,
                eligible_candidates,
            )

        if objective_aware_ordering:
            # SRQ-01 R2: four-step admission sequence (exact analogs first).
            candidates = self._formula_aware_selection(
                cache_key=cache_key,
                material_id=material_id,
                elements_map=elements_map,
                eligible_candidates=eligible_candidates,
                prefer_elements=(
                    normalized_prefer_elements
                    if objective_aware_prefer_allocation
                    else set()
                ),
                avoid_elements=normalized_avoid_elements,
                reject_introduced_avoided=reject_introduced_avoided,
            )
            self._keep_admitted_groups(cache_key, candidates)
            return self._finish_objective_admission(
                cache_key,
                material_id,
                family_result,
                non_test_candidates,
                eligible_candidates,
                candidates,
                missing_membership_excluded,
            )

        selected_indices: set[int] = set()

        if objective_aware_prefer_allocation and normalized_prefer_elements:
            covered_preferred_elements: set[str] = set()

            for preferred_element in sorted(normalized_prefer_elements):
                if preferred_element in covered_preferred_elements:
                    continue

                if len(selected_indices) >= self.EXPANSION_LIMIT:
                    break

                for index, candidate in enumerate(eligible_candidates):
                    if index in selected_indices:
                        continue

                    candidate_elements = set(
                        elements_map.get(candidate["material_id"], [])
                    )

                    if preferred_element not in candidate_elements:
                        continue

                    selected_indices.add(index)
                    covered_preferred_elements.update(
                        candidate_elements.intersection(
                            normalized_prefer_elements
                        )
                    )
                    break

        for index in range(len(eligible_candidates)):
            if len(selected_indices) >= self.EXPANSION_LIMIT:
                break

            selected_indices.add(index)

        candidates = [
            candidate
            for index, candidate in enumerate(eligible_candidates)
            if index in selected_indices
        ]

        return self._finish_objective_admission(
            cache_key,
            material_id,
            family_result,
            non_test_candidates,
            eligible_candidates,
            candidates,
            missing_membership_excluded,
        )

    def _finish_objective_admission(
        self,
        cache_key: tuple,
        material_id: int,
        family_result: dict,
        non_test_candidates: list[dict],
        eligible_candidates: list[dict],
        candidates: list[dict],
        missing_membership_excluded: int,
    ) -> list[dict]:
        self._admission_diagnostics[cache_key] = {
            "missing_membership_excluded": missing_membership_excluded,
        }

        if missing_membership_excluded:
            logger.info(
                "Hard-avoid admission for material {} excluded {} "
                "candidate(s) without element membership",
                material_id,
                missing_membership_excluded,
            )

        self._record_admission_counts(
            cache_key,
            considered=len(non_test_candidates),
            eligible=eligible_candidates,
            admitted=candidates,
        )
        self._candidate_cache[cache_key] = candidates
        return candidates

    def request_compositions(
        self,
    ) -> tuple[dict[int, dict[str, float] | None], dict[int, str | None], dict[int, float | None]]:
        """Stored compositions for every material, loaded once per request (D11).

        Returns (fractions, mp_ids, energy_above_hull) keyed by material ID.
        Each composition passes through normalise_stored_composition; a value
        it rejects maps to None (not evaluated). The process-wide composition
        cache is deliberately not used.
        """
        store = self.__dict__.get("_request_compositions")
        if store is None:
            rows = self.db.execute(
                select(
                    Material.id,
                    Material.mp_id,
                    Material.raw_data["composition"],
                    Material.energy_above_hull,
                )
            ).all()
            fractions: dict[int, dict[str, float] | None] = {}
            mp_ids: dict[int, str | None] = {}
            energies: dict[int, float | None] = {}
            for material_id, mp_id, raw, energy_above_hull in rows:
                mp_ids[material_id] = mp_id
                energies[material_id] = energy_above_hull
                try:
                    fractions[material_id] = normalise_stored_composition(raw)
                except ValueError:
                    fractions[material_id] = None
            store = (fractions, mp_ids, energies)
            self.__dict__["_request_compositions"] = store
        return store

    def _efa_groups_store(self) -> dict:
        return self.__dict__.setdefault("_efa_groups", {})

    def _group_exact_analogs(
        self,
        cache_key: tuple,
        material_id: int,
        eligible_candidates: list[dict],
    ) -> list[dict]:
        """SRQ-01 R3, objective-aware admission only.

        Classifies each eligible candidate against the expanding material,
        groups exact alkali formula analogs by normalised composition, keeps
        only each group's representative and records every group's members.
        Order of the remaining candidates is unchanged.
        """
        fractions, _, energies = self.request_compositions()
        source = fractions.get(material_id)
        groups: list[dict] = []
        if source is not None:
            for candidate in eligible_candidates:
                candidate_fractions = fractions.get(candidate["material_id"])
                if candidate_fractions is None:
                    continue
                result = classify_formula_correspondence(source, candidate_fractions)
                if result is None or result.correspondence_class != "exact_alkali_replacement":
                    continue
                for group in groups:
                    if compositions_equal(group["composition"], candidate_fractions):
                        group["members"].append(candidate)
                        break
                else:
                    groups.append({"composition": candidate_fractions, "members": [candidate]})

        # The representative takes the admission position of the group's
        # earliest member, so which record represents a group never decides
        # whether the group gets a slot (AC11 finding).
        slot_of_group: dict[int, dict] = {}
        grouped_ids: set[int] = set()
        recorded: list[dict] = []
        for group in groups:
            representative = ordering.choose_representative(group["members"])
            slot_of_group[group["members"][0]["material_id"]] = representative
            grouped_ids.update(member["material_id"] for member in group["members"])
            recorded.append({
                "representative_id": representative["material_id"],
                "members": [
                    {
                        "material_id": member["material_id"],
                        "mp_id": member.get("mp_id"),
                        "energy_above_hull": energies.get(member["material_id"]),
                    }
                    for member in group["members"]
                ],
            })
        self._efa_groups_store()[cache_key] = recorded
        kept: list[dict] = []
        for candidate in eligible_candidates:
            material_id = candidate["material_id"]
            if material_id in slot_of_group:
                kept.append(slot_of_group[material_id])
            elif material_id not in grouped_ids:
                kept.append(candidate)
        return kept

    def _keep_admitted_groups(self, cache_key: tuple, admitted: list[dict]) -> None:
        """Keep only groups whose representative was actually admitted (D12).

        Groups are formed before the expansion cap; a group whose
        representative did not win a slot is not an admission group, so its
        members must not be reported for a material reached another way.
        """
        admitted_ids = {candidate["material_id"] for candidate in admitted}
        store = self._efa_groups_store()
        store[cache_key] = [
            group
            for group in store.get(cache_key, [])
            if group["representative_id"] in admitted_ids
        ]

    EFA_GROUP_BUDGET = 4

    def _formula_aware_selection(
        self,
        *,
        cache_key: tuple,
        material_id: int,
        elements_map: dict[int, list[str]],
        eligible_candidates: list[dict],
        prefer_elements: set[str],
        avoid_elements: set[str],
        reject_introduced_avoided: bool,
    ) -> list[dict]:
        """SRQ-01 R2 admission sequence, objective-aware requests only.

        1. Preferred exact analogs: for each preferred element (alphabetical,
           covered rule), the first eligible exact-analog group containing it.
        2. Preferred reservation for still-uncovered preferred elements.
        3. Remaining exact-analog groups, up to EFA_GROUP_BUDGET in total.
        4. General fill in admission order.
        Exact analogs that would introduce an avoided element are not given
        priority (they remain ordinary candidates). Output is in admission
        order. Excluded exact-analog groups are recorded with their reason.
        """
        limit = self.EXPANSION_LIMIT
        index_of = {candidate["material_id"]: index for index, candidate in enumerate(eligible_candidates)}
        groups = self._efa_groups_store().get(cache_key, [])
        source_elements = set(elements_map.get(material_id, []))

        def elements_of(index: int) -> set[str]:
            return set(elements_map.get(eligible_candidates[index]["material_id"], []))

        prioritised: list[int] = []
        for group in groups:
            index = index_of.get(group["representative_id"])
            if index is None:
                continue
            if reject_introduced_avoided and avoid_elements and self.transition_validator._violates_avoid_elements(
                from_elements=source_elements,
                to_elements=elements_of(index),
                avoid_elements=avoid_elements,
            ):
                continue
            prioritised.append(index)

        selected: list[int] = []
        chosen: set[int] = set()
        efa_admitted = 0

        def take(index: int) -> None:
            selected.append(index)
            chosen.add(index)

        covered: set[str] = set()
        for preferred_element in sorted(prefer_elements):  # step 1
            if preferred_element in covered or len(selected) >= limit:
                continue
            for index in prioritised:
                if index in chosen:
                    continue
                candidate_elements = elements_of(index)
                if preferred_element in candidate_elements:
                    take(index)
                    efa_admitted += 1
                    covered.update(candidate_elements & prefer_elements)
                    break

        for preferred_element in sorted(prefer_elements):  # step 2
            if preferred_element in covered or len(selected) >= limit:
                continue
            for index in range(len(eligible_candidates)):
                if index in chosen:
                    continue
                candidate_elements = elements_of(index)
                if preferred_element in candidate_elements:
                    take(index)
                    covered.update(candidate_elements & prefer_elements)
                    break

        for index in prioritised:  # step 3
            if len(selected) >= limit or efa_admitted >= self.EFA_GROUP_BUDGET:
                break
            if index not in chosen:
                take(index)
                efa_admitted += 1

        for index in range(len(eligible_candidates)):  # step 4
            if len(selected) >= limit:
                break
            if index not in chosen:
                take(index)

        excluded = []
        for index in prioritised:
            if index in chosen:
                continue
            representative_id = eligible_candidates[index]["material_id"]
            members = next(g["members"] for g in groups if g["representative_id"] == representative_id)
            excluded.append({
                "display_formula": eligible_candidates[index].get("pretty_formula")
                or eligible_candidates[index].get("formula") or "",
                "member_mp_ids": [member["mp_id"] for member in members if member.get("mp_id")],
                "reason": "efa_budget" if efa_admitted >= self.EFA_GROUP_BUDGET else "cap",
            })
        self.__dict__.setdefault("_efa_expansions", {})[cache_key] = {
            "expanded_material_id": material_id,
            "groups_found": len(groups),
            "groups_admitted": sum(
                1 for group in groups if index_of.get(group["representative_id"]) in chosen
            ),
            "excluded": excluded,
        }
        return [eligible_candidates[index] for index in selected]

    def efa_expansions(self) -> list[dict]:
        """Per-expansion exact-analog counts recorded during this request, in expansion order."""
        return list(self.__dict__.get("_efa_expansions", {}).values())

    def formula_groups_by_representative(self) -> dict[int, list[dict]]:
        """Admission groups recorded during this request, keyed by representative."""
        groups: dict[int, list[dict]] = {}
        for recorded in self._efa_groups_store().values():
            for group in recorded:
                groups.setdefault(group["representative_id"], group["members"])
        return groups

    @staticmethod
    def _admission_order_key(candidate: dict) -> tuple:
        return (
            -len(candidate.get("shared_elements") or []),
            mp_id_sort_key(candidate.get("mp_id"), candidate["material_id"]),
        )

    def _build_transition(
        self,
        from_material: dict,
        to_candidate: dict,
        elements_map: dict[int, list[str]],
        avoid_elements: frozenset[str],
        prefer_elements: frozenset[str],
        reject_introduced_avoided: bool = True,
    ) -> dict | None:
        from_elements = elements_map.get(
            from_material["material_id"],
            [],
        )
        to_elements = elements_map.get(
            to_candidate["material_id"],
            [],
        )

        relationships = self._get_relationships_between(
            from_material_id=from_material["material_id"],
            to_material_id=to_candidate["material_id"],
        )

        return self.transition_validator.validate_transition(
            from_material=from_material,
            to_material=self._candidate_to_node(to_candidate),
            from_elements=from_elements,
            to_elements=to_elements,
            relationships=relationships,
            avoid_elements=avoid_elements,
            prefer_elements=prefer_elements,
            reject_introduced_avoided=reject_introduced_avoided,
        )

    def _get_relationships_between(
        self,
        from_material_id: int,
        to_material_id: int,
    ) -> list[str]:
        cache_key = (from_material_id, to_material_id)

        if cache_key in self._relationship_cache:
            return self._relationship_cache[cache_key]

        family_result = self._get_family_result(from_material_id)
        relationships = []

        for candidate in family_result["related_materials"]:
            if candidate["material_id"] == to_material_id:
                relationships = candidate["relationships"]
                break

        self._relationship_cache[cache_key] = relationships
        return relationships

    def _finalize_chain(self, chain: dict) -> dict:
        return {
            "hop_count": len(chain["transitions"]),
            "materials": chain["materials"],
            "transitions": chain["transitions"],
            "chain_reason": self._build_chain_reason(
                chain["transitions"]
            ),
        }

    def _build_chain_reason(
        self,
        transitions: list[dict],
    ) -> str:
        if not transitions:
            return "No discovery transition was generated."

        transition_types = [
            relationship_text(transition["transition_type"])
            for transition in transitions
        ]

        shared_element_sets = [
            set(
                transition.get("shared_elements")
                or transition.get("preserved_framework", [])
            )
            for transition in transitions
            if (
                transition.get("shared_elements")
                or transition.get("preserved_framework")
            )
        ]

        common_shared_elements = sorted(
            set.intersection(*shared_element_sets)
            if shared_element_sets
            else set()
        )

        reason = (
            "This discovery chain follows "
            + " -> ".join(transition_types)
        )

        if common_shared_elements:
            reason += (
                f" with {'-'.join(common_shared_elements)} "
                "shared-element continuity"
            )

        return reason + "."

    def _get_material_elements_map(
        self,
    ) -> dict[int, list[str]]:
        rows = (
            self.db.query(
                MaterialElement.material_id,
                Element.symbol,
            )
            .join(
                Element,
                MaterialElement.element_id == Element.id,
            )
            .all()
        )

        elements_map: dict[int, set[str]] = {}

        for material_id, symbol in rows:
            elements_map.setdefault(material_id, set()).add(symbol)

        return {
            material_id: sorted(symbols)
            for material_id, symbols in elements_map.items()
        }

    def _material_to_node(
        self,
        material: Material,
    ) -> dict:
        return {
            "material_id": material.id,
            "mp_id": material.mp_id,
            "pretty_formula": material.pretty_formula,
            "formula": material.pretty_formula or material.formula,
        }

    def _candidate_to_node(
        self,
        candidate: dict,
    ) -> dict:
        return {
            "material_id": candidate["material_id"],
            "mp_id": candidate["mp_id"],
            "pretty_formula": candidate["pretty_formula"],
            "formula": (
                candidate["pretty_formula"]
                or candidate["formula"]
            ),
        }

    def _empty_response(
        self,
        material_id: int,
        avoid_element: str | None,
        prefer_element: str | None,
        max_hops: int,
        limit: int,
    ) -> dict:
        return {
            "material_id": material_id,
            "mp_id": None,
            "base_formula": None,
            "discovery_goal": {
                "avoid_element": avoid_element,
                "prefer_element": prefer_element,
                "max_hops": max_hops,
                "limit": limit,
            },
            "search_metadata": {
                "search_policy": "bounded_breadth_first",
                "requested_result_limit": limit,
                "expansion_limit_per_material": self.EXPANSION_LIMIT,
                "search_state_budget": self.SEARCH_STATE_BUDGET,
                "expanded_state_count": 0,
                "generated_chain_count": 0,
                "returned_chain_count": 0,
                "search_truncated": False,
                "result_truncated": False,
                "scientific_completeness_guaranteed": False,
                "expansion_limit_binding": False,
                "expansions_with_cap_discards": 0,
                "candidates_considered_total": 0,
                "candidates_eligible_total": 0,
                "candidates_admitted_total": 0,
                "candidates_discarded_by_expansion_limit_total": 0,
                "distinct_candidates_discarded_by_expansion_limit": 0,
            },
            "chains": [],
        }

    def _get_family_result(
        self,
        material_id: int,
    ) -> dict:
        if material_id not in self._family_result_cache:
            self._family_result_cache[material_id] = (
                self.family_service.get_material_families(
                    material_id
                )
            )

        return self._family_result_cache[material_id]

    def _normalize_elements(
        self,
        *,
        element: str | None,
        elements: Collection[str] | None,
    ) -> frozenset[str]:
        normalized = {
            item
            for item in (elements or [])
            if item
        }

        if element:
            normalized.add(element)

        return frozenset(normalized)