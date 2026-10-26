from app.utils.chemical_formula import contains_element


class DiscoveryWarningService:
    def build_warnings(
        self,
        candidates: list[dict],
        avoid_element: str | None,
        prefer_element: str | None,
        limit: int,
        total_candidate_count: int,
        pool_basis: dict | None = None,
    ) -> list[str]:
        warnings = []

        if not candidates:
            warnings.append(
                "No discovery candidates were found for the requested constraints."
            )
            return warnings

        if prefer_element and not self._any_candidate_contains_element(
            candidates=candidates,
            element=prefer_element,
        ):
            warnings.append(
                f"No returned candidate contains the preferred element {prefer_element}."
            )

        if avoid_element and self._all_candidates_contain_element(
            candidates=candidates,
            element=avoid_element,
        ):
            warnings.append(
                f"All returned candidates still contain the avoided element {avoid_element}."
            )

        if total_candidate_count > limit:
            warnings.append(
                self._limit_warning(limit, total_candidate_count, pool_basis)
            )

        return warnings

    @staticmethod
    def _limit_warning(
        limit: int,
        total_candidate_count: int,
        pool_basis: dict | None,
    ) -> str:
        """State the candidate pool from what each source supplied (R1-fix-839).

        Per-source figures are what each source supplied before
        deduplication; the total is the deduplicated pool before the final
        result limit. No source supplies the source material.
        """
        lead = (
            f"Results were limited to {limit} candidates from "
            f"{total_candidate_count} distinct candidates before the final "
            "result limit was applied"
        )
        if pool_basis is None:
            return lead + "."

        parts = [
            f"composition-related materials supplied "
            f"{pool_basis['composition']} candidates (the source material "
            "excluded)"
        ]
        for key, name in (
            ("recommendation", "recommendation"),
            ("scenario", "scenario"),
        ):
            source = pool_basis.get(key)
            if source is None:
                parts.append(f"{name} candidates were not requested")
            elif source.get("needs_element"):
                parts.append(
                    f"{name} candidates were enabled but none were generated "
                    "for this request, because no avoided or preferred element "
                    "was given"
                )
            elif source["supplied"] == 0:
                parts.append(
                    f"{name} candidates were enabled but none were generated "
                    "for this request"
                )
            else:
                parts.append(
                    f"{name} candidates supplied {source['supplied']} "
                    f"candidates (this source is capped at {source['cap']} "
                    "for this request)"
                )

        supplied = pool_basis["composition"] + sum(
            (pool_basis.get(key) or {}).get("supplied", 0)
            for key in ("recommendation", "scenario")
        )
        overlap = (
            " A candidate supplied by more than one source is counted once in "
            "the total."
            if supplied > total_candidate_count
            else ""
        )
        return f"{lead}: " + "; ".join(parts) + "." + overlap

    def _any_candidate_contains_element(
        self,
        candidates: list[dict],
        element: str,
    ) -> bool:
        return any(
            contains_element(
                candidate.get("pretty_formula") or candidate.get("formula"),
                element,
            )
            for candidate in candidates
        )

    def _all_candidates_contain_element(
        self,
        candidates: list[dict],
        element: str,
    ) -> bool:
        return all(
            contains_element(
                candidate.get("pretty_formula") or candidate.get("formula"),
                element,
            )
            for candidate in candidates
        )