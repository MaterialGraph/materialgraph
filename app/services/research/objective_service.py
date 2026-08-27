from sqlalchemy.orm import Session

from app.services.discovery.chain_service import DiscoveryChainService
from app.services.discovery.path_ranking_service import DiscoveryPathRankingService
from app.services.material.quality_service import MaterialQualityService
from app.utils.chemical_formula import extract_elements


class ResearchObjectiveService:
    def __init__(self, db: Session):
        self.db = db
        self.chain_service = DiscoveryChainService(db)
        self.path_ranking_service = DiscoveryPathRankingService(db)
        self.quality_service = MaterialQualityService(db)

    def generate_chains_for_objective(
        self,
        material_id: int,
        objective,
        include_ranked_pool: bool = False,
    ) -> dict:
        result = self.chain_service.get_discovery_chains(
            material_id=material_id,
            avoid_elements=objective.avoid_elements,
            prefer_elements=objective.prefer_elements,
            max_hops=objective.max_hops,
            limit=objective.limit,
            include_search_pool=True,
        )

        filtered_chains = self._filter_chains(
            chains=result["chains"],
            objective=objective,
        )

        ranked_chains = self._rank_chains(
            chains=filtered_chains,
            objective=objective,
        )
        chains = (
            ranked_chains
            if include_ranked_pool
            else ranked_chains[: objective.limit]
        )
        search_metadata = {
            **result["search_metadata"],
            "returned_chain_count": len(chains),
            "result_truncated": (
                not include_ranked_pool
                and len(ranked_chains) > objective.limit
            ),
        }

        return {
            "material_id": result["material_id"],
            "base_formula": result["base_formula"],
            "objective": objective,
            "objective_policy": self._build_objective_policy(objective),
            "search_metadata": search_metadata,
            "chains": chains,
        }

    def _filter_chains(
        self,
        chains: list[dict],
        objective,
    ) -> list[dict]:
        filtered = []
        quality_by_id = (
            self._quality_for_chains(chains)
            if objective.require_stable_materials
            else {}
        )

        for chain in chains:
            if not self._preserves_required_elements(
                chain,
                objective.preserve_elements,
            ):
                continue

            if not self._matches_target_family(
                chain,
                objective.target_family,
            ):
                continue

            if (
                objective.require_stable_materials
                and not self._has_only_stable_non_root_materials(
                    chain=chain,
                    quality_by_id=quality_by_id,
                )
            ):
                continue

            filtered.append(chain)

        return filtered

    def _preserves_required_elements(
        self,
        chain: dict,
        preserve_elements: list[str],
    ) -> bool:
        required_elements = set(preserve_elements)

        if not required_elements:
            return True

        transitions = chain.get("transitions", [])

        if not transitions:
            return False

        shared_element_sets: list[set[str]] = []

        for transition in transitions:
            if "shared_elements" in transition:
                transition_elements = transition["shared_elements"]
            else:
                transition_elements = transition.get(
                    "preserved_framework",
                    [],
                )

            shared_element_sets.append(set(transition_elements))

        continuous_elements = set.intersection(*shared_element_sets)

        return required_elements.issubset(continuous_elements)

    def _matches_target_family(
        self,
        chain: dict,
        target_family: str | None,
    ) -> bool:
        if target_family is None:
            return True

        materials = chain.get("materials", [])
        if not materials:
            return False

        return self.material_matches_target_family(
            material=materials[-1],
            target_family=target_family,
        )

    @staticmethod
    def material_matches_target_family(
        material: dict,
        target_family: str | None,
    ) -> bool:
        if target_family is None:
            return True

        structured_elements = material.get("elements")
        if structured_elements is None:
            formula = material.get("formula") or material.get("pretty_formula")
            elements = extract_elements(formula) if formula else []
        else:
            elements = structured_elements

        required_elements_by_family = {
            "phosphate": {"P", "O"},
        }
        required_elements = required_elements_by_family.get(
            target_family.strip().lower()
        )

        return (
            required_elements is not None
            and required_elements.issubset(set(elements))
        )

    def _rank_chains(
        self,
        chains: list[dict],
        objective,
    ) -> list[dict]:
        ranked_chains = []

        for chain in chains:
            ranking = self.path_ranking_service.rank_path(
                materials=chain["materials"],
                transitions=chain["transitions"],
                avoid_elements=objective.avoid_elements,
                prefer_elements=objective.prefer_elements,
                prefer_lower_criticality=(
                    objective.prefer_lower_criticality
                ),
            )

            ranked_chains.append({
                **chain,
                **ranking,
            })

        ranked_chains.sort(
            key=lambda item: item["scientific_usefulness_score"],
            reverse=True,
        )

        return ranked_chains

    def _quality_for_chains(
        self,
        chains: list[dict],
    ) -> dict[int, dict]:
        material_ids = list(dict.fromkeys(
            material["material_id"]
            for chain in chains
            for material in chain.get("materials", [])[1:]
            if material.get("material_id") is not None
        ))
        return self.quality_service.get_material_quality_bulk(material_ids)

    @staticmethod
    def _has_only_stable_non_root_materials(
        *,
        chain: dict,
        quality_by_id: dict[int, dict],
    ) -> bool:
        non_root_materials = chain.get("materials", [])[1:]
        if not non_root_materials:
            return False

        return all(
            quality_by_id.get(
                material.get("material_id"),
                {},
            ).get("stability_band") == "stable"
            for material in non_root_materials
        )

    @staticmethod
    def _build_objective_policy(objective) -> dict:
        return {
            "stable_materials": (
                "hard_rejection"
                if objective.require_stable_materials
                else "not_required"
            ),
            "stability_scope": (
                "all_non_root_chain_materials"
                if objective.require_stable_materials
                else "none"
            ),
            "stability_evidence_policy": (
                "canonical_energy_primary_with_imported_flag_fallback"
            ),
            "unknown_stability_evidence": (
                "hard_rejection"
                if objective.require_stable_materials
                else "not_applicable"
            ),
            "lower_criticality": (
                "canonical_quality_preference"
                if objective.prefer_lower_criticality
                else "excluded_from_objective_ranking"
            ),
            "unknown_criticality_evidence": "no_criticality_credit",
        }