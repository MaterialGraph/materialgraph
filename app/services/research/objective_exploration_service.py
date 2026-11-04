from sqlalchemy.orm import Session

from app.domain.objective_mode_policy import mode_policy
from app.domain.relationship_labels import relationship_text
from app.services.material.quality_service import MaterialQualityService
from app.services.research.formula_correspondence_report import (
    build_formula_correspondence_report,
    classify_chain_transitions,
    correspondence_relationship_text,
    mp_id_sort_key,
    source_efa_material_ids,
)
from app.services.research.objective_coverage import build_objective_coverage
from app.services.research.objective_service import ResearchObjectiveService
from app.utils.chemical_formula import contains_element


class ResearchObjectiveExplorationService:
    def __init__(self, db: Session):
        self.db = db
        self.objective_service = ResearchObjectiveService(db)
        self.quality_service = MaterialQualityService(db)

    def explore(self, material_id: int, request) -> dict:
        # Contract P: every avoid and prefer behaviour below is read from the
        # mode's policy object.
        policy = mode_policy(request.mode)
        # Transition validation rejects introduced avoided elements unless told
        # otherwise; the flag is forwarded only when a mode's policy differs
        # from that default (no current mode does).
        transition_policy = (
            {}
            if policy.reject_introduced_avoided
            else {"reject_introduced_avoided": False}
        )
        # SRQ-01 R5: MP-ID ordering on objective-aware requests only. Frozen
        # requests forward no ordering arguments, so their calls are unchanged.
        objective_aware = self.is_objective_aware(request)
        ordering_policy = (
            {"objective_aware_ordering": True, "chain_tie_key": self.chain_tie_key}
            if objective_aware
            else {}
        )
        chain_result = self.objective_service.generate_chains_for_objective(
            material_id=material_id,
            objective=request.objective,
            include_ranked_pool=True,
            hard_avoid_admission=policy.hard_avoid_admission,
            objective_aware_prefer_allocation=(
                policy.objective_aware_prefer_allocation
            ),
            **transition_policy,
            **ordering_policy,
        )

        chains = chain_result.get("chains", [])
        eligible_chains = self._apply_mode_constraints(
            chains=chains,
            objective=request.objective,
            mode=request.mode,
        )
        # Objective-aware requests label classified alkali steps in reasons
        # (SRQ-01); frozen requests keep today's wording. Read-only: scores,
        # ranking and ordering are unaffected.
        pair_correspondence = (
            classify_chain_transitions(self.db, eligible_chains)
            if self.is_objective_aware(request) and self.db is not None
            else None
        )
        candidates = self._rank_candidates_from_chains(
            chains=eligible_chains,
            objective=request.objective,
            mode=request.mode,
            pair_correspondence=pair_correspondence,
            source_material_id=material_id if objective_aware else None,
        )
        chains = eligible_chains[: request.limit]
        search_metadata = {
            **chain_result["search_metadata"],
            "returned_chain_count": len(chains),
            "result_truncated": len(eligible_chains) > request.limit,
        }

        returned_candidates = candidates[: request.limit]
        objective_coverage = build_objective_coverage(
            material_id=material_id,
            base_formula=chain_result.get("base_formula"),
            objective=request.objective,
            mode=request.mode,
            ranked_candidates=returned_candidates,
            chains=chains,
            ranked_material_pool_count=len(candidates),
            result_truncated=bool(search_metadata.get("result_truncated")),
            search_truncated=bool(search_metadata.get("search_truncated")),
        )

        response = {
            "material_id": material_id,
            "base_formula": chain_result.get("base_formula"),
            "objective": request.objective,
            "objective_policy": chain_result["objective_policy"],
            "mode": request.mode,
            "constraint_policy": policy.constraint_policy(),
            "avoid_policy": policy.avoid_policy(),
            "prefer_policy": policy.prefer_policy(),
            "candidate_score_offset": policy.candidate_score_offset,
            "search_metadata": search_metadata,
            "ranked_candidates": returned_candidates,
            "chains": chains,
            "warnings": self._build_global_warnings(request.mode),
            "explanation": self._build_explanation(request.mode),
            "objective_coverage": objective_coverage,
        }
        # Read-only report on what was already returned (SRQ-01 R7.1); frozen
        # requests carry no key at all.
        if self.is_objective_aware(request):
            response["formula_correspondence"] = build_formula_correspondence_report(
                self.db,
                source_material_id=material_id,
                chains=chains,
                ranked_candidates=returned_candidates,
            )
        return response

    @staticmethod
    def chain_tie_key(chain: dict) -> tuple:
        """R5: MP-ID keys of the chain's ordered materials, source included."""
        return tuple(
            mp_id_sort_key(material.get("mp_id"), material["material_id"])
            for material in chain.get("materials", [])
        )

    @staticmethod
    def is_objective_aware(request) -> bool:
        """Spec rev 3.7, 4.0: at least one preferred element, or Strict with
        at least one avoided element. Every other request is frozen."""
        # Partial objective objects (test doubles, older callers) count a
        # missing term as not requested, as objective coverage does.
        objective = request.objective
        prefer_elements = getattr(objective, "prefer_elements", None) or ()
        avoid_elements = getattr(objective, "avoid_elements", None) or ()
        return bool(prefer_elements) or (
            request.mode == "strict" and bool(avoid_elements)
        )

    def _apply_mode_constraints(
        self,
        chains: list[dict],
        objective,
        mode: str,
    ) -> list[dict]:
        if (
            not mode_policy(mode).applies_final_filter
            or not objective.avoid_elements
        ):
            return chains

        return [
            chain
            for chain in chains
            if self._chain_satisfies_strict_avoidance(
                chain=chain,
                avoid_elements=objective.avoid_elements,
            )
        ]

    def _chain_satisfies_strict_avoidance(
        self,
        chain: dict,
        avoid_elements: list[str],
    ) -> bool:
        materials = chain.get("materials", [])

        return all(
            not self._material_contains_any_element(material, avoid_elements)
            for material in materials[1:]
        )

    def _material_contains_any_element(
        self,
        material: dict,
        elements: list[str],
    ) -> bool:
        formula = material.get("formula") or material.get("pretty_formula") or ""
        return any(contains_element(formula, element) for element in elements)

    def _rank_candidates_from_chains(
        self,
        chains,
        objective,
        mode: str,
        pair_correspondence: dict | None = None,
        source_material_id: int | None = None,
    ) -> list[dict]:
        candidate_map: dict[int, dict] = {}
        quality_by_id = (
            self._quality_for_candidates(chains)
            if objective.prefer_lower_criticality
            else {}
        )

        for chain in chains:
            materials = chain.get("materials", [])
            transitions = chain.get("transitions", [])

            for material_index, material in enumerate(
                materials[1:],
                start=1,
            ):
                material_id = material["material_id"]
                attribution_transitions = transitions[:material_index]

                if material_id not in candidate_map:
                    candidate_map[material_id] = {
                        "material_id": material_id,
                        # Distinguishes same-formula records (R1-6).
                        "mp_id": material.get("mp_id"),
                        "formula": material.get("formula") or material.get("pretty_formula"),
                        "score": 0.0,
                        "reasons": [],
                        "warnings": [],
                    }

                candidate = candidate_map[material_id]
                score = self._score_material(
                    material=material,
                    transitions=attribution_transitions,
                    objective=objective,
                    mode=mode,
                    quality=quality_by_id.get(material_id, {}),
                )

                candidate["score"] = max(candidate["score"], score)

                candidate["reasons"].extend(
                    self._build_reasons(
                        material=material,
                        transitions=attribution_transitions,
                        objective=objective,
                        quality=quality_by_id.get(material_id, {}),
                        pair_correspondence=pair_correspondence,
                    )
                )

                candidate["warnings"].extend(
                    self._build_candidate_warnings(
                        material=material,
                        objective=objective,
                        mode=mode,
                    )
                )

                candidate["reasons"] = list(dict.fromkeys(candidate["reasons"]))
                candidate["warnings"] = list(dict.fromkeys(candidate["warnings"]))

        if source_material_id is None:
            return sorted(
                candidate_map.values(),
                key=lambda item: item["score"],
                reverse=True,
            )

        # R5b/R6 on objective-aware requests: among equal scores, source
        # analogs first, then numeric MP ID. Scores are unchanged.
        source_analogs = (
            source_efa_material_ids(self.db, source_material_id, candidate_map)
            if self.db is not None
            else set()
        )
        return sorted(
            candidate_map.values(),
            key=lambda item: (
                -item["score"],
                item["material_id"] not in source_analogs,
                mp_id_sort_key(item.get("mp_id"), item["material_id"]),
            ),
        )

    def _score_material(
        self,
        material,
        transitions,
        objective,
        mode: str,
        quality: dict | None = None,
    ) -> float:
        policy = mode_policy(mode)
        score = 50.0

        formula = material.get("formula", "")

        for element in objective.prefer_elements:
            if contains_element(formula, element):
                score += policy.prefer.candidate_bonus_per_element

        for element in objective.avoid_elements:
            if contains_element(formula, element):
                score -= policy.avoid.candidate_penalty

        for transition in transitions:
            preserved = set(transition.get("shared_elements") or transition.get("preserved_framework", []))
            required = set(objective.preserve_elements)

            if required and required.issubset(preserved):
                score += 20.0

        if (
            objective.target_family is not None
            and self.objective_service.material_matches_target_family(
                material=material,
                target_family=objective.target_family,
            )
        ):
            score += 10.0

        score += policy.candidate_score_offset

        if objective.prefer_lower_criticality:
            score += (quality or {}).get(
                "criticality_quality_contribution",
                0.0,
            )

        return round(score, 2)

    def _build_reasons(
        self,
        material,
        transitions,
        objective,
        quality: dict | None = None,
        pair_correspondence: dict | None = None,
    ) -> list[str]:
        reasons = []

        formula = material.get("formula", "")

        for element in objective.prefer_elements:
            if contains_element(formula, element):
                reasons.append(f"Candidate contains preferred element {element}.")

        for transition in transitions:
            transition_type = transition.get("transition_type")
            if transition_type:
                # Classified pairs are exactly the one-alkali-change pairs the
                # formula-correspondence report labels; any other step keeps
                # its existing wording.
                entry = (
                    pair_correspondence.get(
                        (transition.get("from_material_id"), transition.get("to_material_id"))
                    )
                    if pair_correspondence
                    else None
                )
                # A classified step describes that step, which may come before
                # this material in the chain; the wording says so.
                if entry:
                    reasons.append(
                        "Appears in an eligible composition chain containing a step "
                        f"classified as {correspondence_relationship_text(entry)}."
                    )
                else:
                    reasons.append(
                        "Appears in an eligible composition chain with relationship "
                        f"type {relationship_text(transition_type)}."
                    )

            shared_elements = transition.get("shared_elements") or transition.get("preserved_framework", [])
            if shared_elements:
                reasons.append(
                    "Shares elements across the composition relationship: "
                    f"{', '.join(shared_elements)}. "
                    "Structural preservation is not validated."
                )

        criticality_contribution = (quality or {}).get(
            "criticality_quality_contribution",
            0.0,
        )
        if objective.prefer_lower_criticality and criticality_contribution:
            reasons.append(
                "Lower-criticality preference contributes "
                f"{criticality_contribution:.1f} through canonical material "
                "quality evidence."
            )

        return list(dict.fromkeys(reasons))

    def _quality_for_candidates(self, chains: list[dict]) -> dict[int, dict]:
        material_ids = list(dict.fromkeys(
            material["material_id"]
            for chain in chains
            for material in chain.get("materials", [])[1:]
            if material.get("material_id") is not None
        ))
        return self.quality_service.get_material_quality_bulk(material_ids)

    def _build_candidate_warnings(self, material, objective, mode: str) -> list[str]:
        warnings = []

        formula = material.get("formula", "")

        for element in objective.avoid_elements:
            if contains_element(formula, element):
                message = f"Candidate still contains avoided element {element}."
                warnings.append(message)

        return warnings

    def _build_global_warnings(self, mode: str) -> list[str]:
        # Generated from the policy object (contract P-3, P-5).
        return [mode_policy(mode).warning()]

    def _build_explanation(self, mode: str) -> str:
        return (
            "Research Objective Exploration combines existing objective chains, "
            "scientific transitions, shared-element continuity, preferred elements, "
            "avoid-element warnings, and exploration mode into a ranked research view. "
            f"Current mode: {mode}."
        )
