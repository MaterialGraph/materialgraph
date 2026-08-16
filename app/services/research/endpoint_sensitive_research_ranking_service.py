from app.services.research.scientific_score_semantics import (
    normalize_scientific_usefulness_score,
)


class EndpointSensitiveResearchRankingService:
    """Analyze same-score pathway groups using endpoint-specific evidence.

    This service intentionally does not replace or mutate the existing
    scientific_usefulness_score. It only explains whether existing endpoint
    evidence can justify deterministic differentiation inside score ties.
    """

    EVIDENCE_READINESS_ORDER = {
        "strong": 3,
        "moderate": 2,
        "limited": 1,
    }
    ORDERING_DIMENSIONS = [
        "endpoint_quality_score",
        "endpoint_stability_score",
        "endpoint_energy_above_hull_band",
        "endpoint_criticality_band",
        "endpoint_risk_band",
        "evidence_readiness",
    ]
    GROUPING_POLICY = {
        "endpoint_quality_score": "two_decimal_producer_precision",
        "endpoint_stability_score": "two_decimal_producer_precision",
        "endpoint_energy_above_hull": "quality_policy_threshold_bands",
        "endpoint_criticality_score": "quality_policy_threshold_bands",
        "endpoint_risk_score": "quality_policy_threshold_bands",
        "evidence_readiness": "categorical_readiness",
    }

    def rank_opportunities(self, opportunities: list[dict]) -> dict:
        if not opportunities:
            return self._empty_result()

        score_groups = self._group_by_scientific_score(opportunities)
        groups = [
            self._analyze_score_group(score, group)
            for score, group in sorted(score_groups.items(), reverse=True)
        ]

        differentiated_groups = [
            group
            for group in groups
            if group["differentiation_status"] == "endpoint_differentiated"
        ]

        preserved_tie_groups = [
            group
            for group in groups
            if group["differentiation_status"] == "tie_preserved"
        ]

        return {
            "ranking_basis": "endpoint_specific_existing_evidence",
            "ordering_policy": "lexicographic",
            "ordering_dimensions": list(self.ORDERING_DIMENSIONS),
            "evidence_grouping_policy": dict(self.GROUPING_POLICY),
            "score_preserved": True,
            "original_score_field": "scientific_usefulness_score",
            "endpoint_sensitive_score_added": False,
            "differentiated_group_count": len(differentiated_groups),
            "preserved_tie_group_count": len(preserved_tie_groups),
            "groups": groups,
            "researcher_decision_required": True,
            "decision_boundary": (
                "Endpoint-sensitive ranking only compares existing endpoint-specific "
                "quality, risk, stability, and evidence-readiness signals. It does not "
                "claim synthesis feasibility, electrochemical performance, or experimental "
                "validity. Researchers remain responsible for final scientific judgement."
            ),
        }

    def _group_by_scientific_score(self, opportunities: list[dict]) -> dict[float, list[dict]]:
        groups: dict[float, list[dict]] = {}

        for opportunity in opportunities:
            score = normalize_scientific_usefulness_score(
                opportunity.get("scientific_usefulness_score")
            )
            groups.setdefault(score, []).append(opportunity)

        return groups

    def _analyze_score_group(self, score: float, opportunities: list[dict]) -> dict:
        endpoint_records = [
            self._endpoint_record(opportunity)
            for opportunity in opportunities
        ]

        if len(endpoint_records) <= 1:
            return {
                "scientific_usefulness_score": score,
                "pathway_count": len(endpoint_records),
                "differentiation_status": "single_pathway",
                "tie_preserved": False,
                "reason": "Only one pathway has this scientific usefulness score.",
                "endpoint_records": endpoint_records,
            }

        evidence_groups = self._group_by_endpoint_evidence(endpoint_records)

        if len(evidence_groups) == 1:
            return {
                "scientific_usefulness_score": score,
                "pathway_count": len(endpoint_records),
                "differentiation_status": "tie_preserved",
                "tie_preserved": True,
                "reason": (
                    "Pathways share the same scientific usefulness score and current "
                    "endpoint-specific evidence does not justify deterministic ordering."
                ),
                "endpoint_records": endpoint_records,
            }

        ordered_groups = sorted(
            evidence_groups,
            key=lambda group: group["sort_key"],
            reverse=True,
        )

        endpoint_priority_groups = []
        for index, group in enumerate(ordered_groups, start=1):
            endpoint_priority_groups.append({
                "endpoint_sensitive_group_rank": index,
                "shared_endpoint_evidence": group["evidence"],
                "pathways": group["records"],
                "reason": self._group_reason(group["evidence"]),
            })

        return {
            "scientific_usefulness_score": score,
            "pathway_count": len(endpoint_records),
            "differentiation_status": "endpoint_differentiated",
            "tie_preserved": False,
            "reason": (
                "Pathways share the same scientific usefulness score, but endpoint-specific "
                "existing evidence differs enough to support deterministic within-tie grouping."
            ),
            "ordering_policy": "lexicographic",
            "ordering_dimensions": list(self.ORDERING_DIMENSIONS),
            "endpoint_priority_groups": endpoint_priority_groups,
        }

    def _endpoint_record(self, opportunity: dict) -> dict:
        endpoint = self._endpoint_material(opportunity)
        endpoint_quality = self._endpoint_quality(opportunity, endpoint)
        evidence_readiness = self._evidence_readiness(opportunity)

        return {
            "pathway_rank": opportunity.get("rank"),
            "endpoint_material": endpoint,
            "endpoint_evidence": {
                "endpoint_quality_score": endpoint_quality.get("quality_score"),
                "endpoint_stability_score": endpoint_quality.get("stability_score"),
                "endpoint_energy_above_hull": endpoint_quality.get("energy_above_hull"),
                "endpoint_criticality_score": endpoint_quality.get("criticality_score"),
                "endpoint_risk_score": endpoint_quality.get("risk_score"),
                "evidence_readiness": evidence_readiness,
            },
            "requires_validation": True,
        }

    def _endpoint_material(self, opportunity: dict) -> dict | None:
        materials = opportunity.get("pathway", {}).get("materials", [])

        if not materials:
            return None

        endpoint = materials[-1]

        return {
            "material_id": endpoint.get("material_id"),
            "formula": endpoint.get("formula"),
            "pretty_formula": endpoint.get("pretty_formula"),
            "mp_id": endpoint.get("mp_id"),
        }

    def _endpoint_quality(self, opportunity: dict, endpoint: dict | None) -> dict:
        if endpoint is None:
            return {}

        endpoint_material_id = endpoint.get("material_id")
        quality_items = opportunity.get("scientific_facts", {}).get("material_quality", [])

        for quality in quality_items:
            if quality.get("material_id") == endpoint_material_id:
                return quality

        return {}

    def _evidence_readiness(self, opportunity: dict) -> str:
        return opportunity.get("evidence_summary", {}).get(
            "evidence_readiness",
            "limited",
        )

    def _group_by_endpoint_evidence(self, endpoint_records: list[dict]) -> list[dict]:
        groups_by_key: dict[tuple, dict] = {}

        for record in endpoint_records:
            evidence = record["endpoint_evidence"]
            sort_key = self._endpoint_evidence_sort_key(evidence)
            equality_key = self._endpoint_evidence_equality_key(evidence)
            grouping_evidence = self._endpoint_evidence_grouping_view(
                evidence
            )

            if equality_key not in groups_by_key:
                groups_by_key[equality_key] = {
                    "sort_key": sort_key,
                    "evidence": grouping_evidence,
                    "records": [],
                }

            groups_by_key[equality_key]["records"].append(record)

        return list(groups_by_key.values())

    def _endpoint_evidence_equality_key(self, evidence: dict) -> tuple:
        grouping_evidence = self._endpoint_evidence_grouping_view(evidence)
        return tuple(
            grouping_evidence.get(dimension)
            for dimension in self.ORDERING_DIMENSIONS
        )

    def _endpoint_evidence_sort_key(self, evidence: dict) -> tuple:
        grouping_evidence = self._endpoint_evidence_grouping_view(evidence)
        return (
            self._value_or_floor(
                grouping_evidence.get("endpoint_quality_score")
            ),
            self._value_or_floor(
                grouping_evidence.get("endpoint_stability_score")
            ),
            grouping_evidence.get("endpoint_energy_above_hull_band_rank", 0),
            grouping_evidence.get("endpoint_criticality_band_rank", 0),
            grouping_evidence.get("endpoint_risk_band_rank", 0),
            self.EVIDENCE_READINESS_ORDER.get(
                grouping_evidence.get("evidence_readiness"),
                0,
            ),
        )

    def _endpoint_evidence_grouping_view(self, evidence: dict) -> dict:
        energy_band, energy_rank = self._lower_value_band(
            evidence.get("endpoint_energy_above_hull"),
            thresholds=(0.01, 0.05, 0.1),
        )
        criticality_band, criticality_rank = self._lower_value_band(
            evidence.get("endpoint_criticality_score"),
            thresholds=(30.0, 60.0),
        )
        risk_band, risk_rank = self._lower_value_band(
            evidence.get("endpoint_risk_score"),
            thresholds=(3.0, 6.0),
        )

        return {
            "endpoint_quality_score": self._two_decimal_value(
                evidence.get("endpoint_quality_score")
            ),
            "endpoint_stability_score": self._two_decimal_value(
                evidence.get("endpoint_stability_score")
            ),
            "endpoint_energy_above_hull_band": energy_band,
            "endpoint_energy_above_hull_band_rank": energy_rank,
            "endpoint_criticality_band": criticality_band,
            "endpoint_criticality_band_rank": criticality_rank,
            "endpoint_risk_band": risk_band,
            "endpoint_risk_band_rank": risk_rank,
            "evidence_readiness": evidence.get("evidence_readiness"),
        }

    def _two_decimal_value(
        self,
        value: float | int | None,
    ) -> float | None:
        if value is None:
            return None
        return round(float(value), 2)

    def _lower_value_band(
        self,
        value: float | int | None,
        *,
        thresholds: tuple[float, ...],
    ) -> tuple[str, int]:
        if value is None:
            return "unknown", 0

        numeric_value = float(value)
        band_count = len(thresholds) + 1

        for index, threshold in enumerate(thresholds):
            if numeric_value <= threshold:
                return f"at_most_{threshold:g}", band_count - index

        return f"above_{thresholds[-1]:g}", 1

    def _value_or_floor(self, value: float | int | None) -> float:
        if value is None:
            return -1.0
        return float(value)

    def _lower_is_better(self, value: float | int | None) -> float:
        if value is None:
            return -1_000_000.0
        return -float(value)

    def _group_reason(self, evidence: dict) -> str:
        reasons = []

        quality_score = evidence.get("endpoint_quality_score")
        stability_score = evidence.get("endpoint_stability_score")
        energy_band = evidence.get("endpoint_energy_above_hull_band")
        criticality_band = evidence.get("endpoint_criticality_band")
        risk_band = evidence.get("endpoint_risk_band")
        evidence_readiness = evidence.get("evidence_readiness")

        if quality_score is not None:
            reasons.append(f"endpoint quality score {quality_score}")
        if stability_score is not None:
            reasons.append(f"endpoint stability score {stability_score}")
        if energy_band is not None:
            reasons.append(f"endpoint energy-above-hull band {energy_band}")
        if criticality_band is not None:
            reasons.append(f"endpoint criticality band {criticality_band}")
        if risk_band is not None:
            reasons.append(f"endpoint risk band {risk_band}")
        if evidence_readiness:
            reasons.append(f"evidence readiness {evidence_readiness}")

        if not reasons:
            return "Endpoint-specific evidence is unavailable; no scientific preference is inferred."

        return "Endpoint-sensitive grouping is based on " + "; ".join(reasons) + "."

    def _empty_result(self) -> dict:
        return {
            "ranking_basis": "endpoint_specific_existing_evidence",
            "ordering_policy": "lexicographic",
            "ordering_dimensions": list(self.ORDERING_DIMENSIONS),
            "evidence_grouping_policy": dict(self.GROUPING_POLICY),
            "score_preserved": True,
            "original_score_field": "scientific_usefulness_score",
            "endpoint_sensitive_score_added": False,
            "differentiated_group_count": 0,
            "preserved_tie_group_count": 0,
            "groups": [],
            "researcher_decision_required": True,
            "decision_boundary": (
                "No pathway opportunities were available for endpoint-sensitive ranking."
            ),
        }