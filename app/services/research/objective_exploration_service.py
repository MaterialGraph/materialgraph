from sqlalchemy.orm import Session

from app.services.research.objective_service import ResearchObjectiveService
from app.utils.chemical_formula import contains_element


class ResearchObjectiveExplorationService:
    def __init__(self, db: Session):
        self.db = db
        self.objective_service = ResearchObjectiveService(db)

    def explore(self, material_id: int, request) -> dict:
        chain_result = self.objective_service.generate_chains_for_objective(
            material_id=material_id,
            objective=request.objective,
            include_ranked_pool=True,
        )

        chains = chain_result.get("chains", [])
        eligible_chains = self._apply_mode_constraints(
            chains=chains,
            objective=request.objective,
            mode=request.mode,
        )
        candidates = self._rank_candidates_from_chains(
            chains=eligible_chains,
            objective=request.objective,
            mode=request.mode,
        )
        chains = eligible_chains[: request.limit]
        search_metadata = {
            **chain_result["search_metadata"],
            "returned_chain_count": len(chains),
            "result_truncated": len(eligible_chains) > request.limit,
        }

        return {
            "material_id": material_id,
            "base_formula": chain_result.get("base_formula"),
            "objective": request.objective,
            "mode": request.mode,
            "constraint_policy": self._build_constraint_policy(request.mode),
            "search_metadata": search_metadata,
            "ranked_candidates": candidates[: request.limit],
            "chains": chains,
            "warnings": self._build_global_warnings(request.mode),
            "explanation": self._build_explanation(request.mode),
        }

    def _apply_mode_constraints(
        self,
        chains: list[dict],
        objective,
        mode: str,
    ) -> list[dict]:
        if mode != "strict" or not objective.avoid_elements:
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

    def _build_constraint_policy(self, mode: str) -> dict[str, str]:
        if mode == "strict":
            return {
                "avoid_elements": "hard_rejection",
                "prefer_elements": "soft_bonus",
                "hard_rejection_scope": "all_non_root_chain_materials",
            }

        return {
            "avoid_elements": "soft_penalty",
            "prefer_elements": "soft_bonus",
            "hard_rejection_scope": "none",
        }

    def _rank_candidates_from_chains(self, chains, objective, mode: str) -> list[dict]:
        candidate_map: dict[int, dict] = {}

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
                )

                candidate["score"] = max(candidate["score"], score)

                candidate["reasons"].extend(
                    self._build_reasons(
                        material=material,
                        transitions=attribution_transitions,
                        objective=objective,
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

        return sorted(
            candidate_map.values(),
            key=lambda item: item["score"],
            reverse=True,
        )

    def _score_material(self, material, transitions, objective, mode: str) -> float:
        score = 50.0

        formula = material.get("formula", "")

        for element in objective.prefer_elements:
            if contains_element(formula, element):
                score += 15.0

        for element in objective.avoid_elements:
            if contains_element(formula, element):
                score -= 25.0 if mode != "exploratory" else 10.0

        for transition in transitions:
            preserved = set(transition.get("shared_elements") or transition.get("preserved_framework", []))
            required = set(objective.preserve_elements)

            if required and required.issubset(preserved):
                score += 20.0

            if transition.get("transition_type") == "alkali_substitution":
                score += 10.0

        if (
            objective.target_family is not None
            and self.objective_service.material_matches_target_family(
                material=material,
                target_family=objective.target_family,
            )
        ):
            score += 10.0

        if mode == "exploratory":
            score += 5.0

        return round(score, 2)

    def _build_reasons(self, material, transitions, objective) -> list[str]:
        reasons = []

        formula = material.get("formula", "")

        for element in objective.prefer_elements:
            if contains_element(formula, element):
                reasons.append(f"Candidate contains preferred element {element}.")

        for transition in transitions:
            transition_type = transition.get("transition_type")
            if transition_type:
                reasons.append(f"Connected through {transition_type} pathway.")

            shared_elements = transition.get("shared_elements") or transition.get("preserved_framework", [])
            if shared_elements:
                reasons.append(
                    f"Shares elements across the transition: {', '.join(shared_elements)}. "
                    "Structural preservation is not validated."
                )

        return list(dict.fromkeys(reasons))

    def _build_candidate_warnings(self, material, objective, mode: str) -> list[str]:
        warnings = []

        formula = material.get("formula", "")

        for element in objective.avoid_elements:
            if contains_element(formula, element):
                message = f"Candidate still contains avoided element {element}."
                warnings.append(message)

        return warnings

    def _build_global_warnings(self, mode: str) -> list[str]:
        if mode == "exploratory":
            return [
                "Exploratory mode includes weaker or unusual candidates for broader scientific search."
            ]

        if mode == "strict":
            return [
                "Strict mode is intended for explicit hard constraints and may exclude scientifically interesting candidates."
            ]

        return [
            "Balanced mode ranks, explains, and warns without aggressively discarding candidates."
        ]

    def _build_explanation(self, mode: str) -> str:
        return (
            "Research Objective Exploration combines existing objective chains, "
            "scientific transitions, shared-element continuity, preferred elements, "
            "avoid-element warnings, and exploration mode into a ranked research view. "
            f"Current mode: {mode}."
        )