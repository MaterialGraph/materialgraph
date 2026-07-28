from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.schemas.substitution import (
    SubstituteCandidate,
    SubstitutionRequest,
    SubstitutionResult,
)
from app.services.material.risk_service import MaterialRiskService


class SubstitutionAnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.material_risk_service = MaterialRiskService(db)

    def analyze(
        self,
        request: SubstitutionRequest,
    ) -> SubstitutionResult | None:
        source = (
            self.db.query(Material)
            .filter(Material.id == request.material_id)
            .first()
        )

        if source is None:
            return None

        source_elements = self._get_element_symbols(source.id)
        source_risk_signal = self.material_risk_service.get_material_risk_signal(
            source.id
        )
        source_risk = self._known_risk_score(source_risk_signal)

        candidates = []

        for material in self.db.query(Material).filter(Material.id != source.id).all():
            candidate_elements = self._get_element_symbols(material.id)

            if not candidate_elements:
                continue

            similarity = self._jaccard_similarity(
                source_elements,
                candidate_elements,
            )

            if similarity == 0:
                continue

            risk_signal = self.material_risk_service.get_material_risk_signal(
                material.id
            )
            candidate_risk = self._known_risk_score(risk_signal)

            # Unknown risk contributes no evidence-derived benefit. In
            # particular, it must not be converted to numeric zero and receive
            # the maximum low-risk component.
            risk_component = (
                max(0.0, (10.0 - candidate_risk) / 10.0)
                if candidate_risk is not None
                else 0.0
            )

            stability_bonus = 0.05 if material.is_stable else 0.0

            rank_score = (
                (similarity * 0.7)
                + (risk_component * 0.3)
                + stability_bonus
            )

            shared_elements = sorted(source_elements.intersection(candidate_elements))
            replacement_elements = sorted(candidate_elements - source_elements)
            removed_elements = sorted(source_elements - candidate_elements)

            candidates.append(
                SubstituteCandidate(
                    material_id=material.id,
                    formula=material.formula,
                    pretty_formula=material.pretty_formula,
                    similarity_score=round(similarity, 3),
                    material_risk_score=(
                        round(candidate_risk, 3)
                        if candidate_risk is not None
                        else None
                    ),
                    risk_known=bool(risk_signal.get("risk_known")),
                    risk_profile_coverage=risk_signal.get(
                        "risk_profile_coverage",
                        0.0,
                    ),
                    risk_evidence_complete=bool(
                        risk_signal.get("risk_evidence_complete")
                    ),
                    unknown_risk_elements=risk_signal.get(
                        "unknown_risk_elements",
                        [],
                    ),
                    rank_score=round(rank_score, 3),
                    shared_elements=shared_elements,
                    replacement_elements=replacement_elements,
                    removed_elements=removed_elements,
                    explanation=self._build_explanation(
                        candidate=material,
                        shared_elements=shared_elements,
                        replacement_elements=replacement_elements,
                        removed_elements=removed_elements,
                        source_risk=source_risk,
                        candidate_risk=candidate_risk,
                    ),
                )
            )

        # Known risk evidence is a primary decision dimension. Rank score then
        # orders candidates within the evidence tier, followed by a stable ID
        # tie-break so database row order cannot change the result.
        ranked = sorted(
            candidates,
            key=lambda item: (
                item.risk_known,
                item.rank_score,
                -item.material_id,
            ),
            reverse=True,
        )

        top_substitutes = ranked[: request.top_n]

        logger.info(
            "Generated {} substitutes for material {}",
            len(top_substitutes),
            source.id,
        )

        return SubstitutionResult(
            source_material_id=source.id,
            source_formula=source.pretty_formula,
            source_risk_score=(
                round(source_risk, 3)
                if source_risk is not None
                else None
            ),
            source_risk_known=bool(source_risk_signal.get("risk_known")),
            source_risk_profile_coverage=source_risk_signal.get(
                "risk_profile_coverage",
                0.0,
            ),
            source_risk_evidence_complete=bool(
                source_risk_signal.get("risk_evidence_complete")
            ),
            source_unknown_risk_elements=source_risk_signal.get(
                "unknown_risk_elements",
                [],
            ),
            substitutes=top_substitutes,
        )

    def _known_risk_score(self, risk_signal: dict) -> float | None:
        if not risk_signal.get("risk_known"):
            return None

        return risk_signal.get("risk_score")

    def _get_element_symbols(self, material_id: int) -> set[str]:
        rows = (
            self.db.query(Element.symbol)
            .join(MaterialElement, Element.id == MaterialElement.element_id)
            .filter(MaterialElement.material_id == material_id)
            .all()
        )

        return {row[0] for row in rows}

    def _jaccard_similarity(
        self,
        source_elements: set[str],
        candidate_elements: set[str],
    ) -> float:
        union = source_elements.union(candidate_elements)

        if not union:
            return 0.0

        return len(source_elements.intersection(candidate_elements)) / len(union)

    def _build_explanation(
        self,
        candidate: Material,
        shared_elements: list[str],
        replacement_elements: list[str],
        removed_elements: list[str],
        source_risk: float | None,
        candidate_risk: float | None,
    ) -> str:
        parts = []

        if shared_elements:
            parts.append(f"Shares chemistry through {'-'.join(shared_elements)}")

        if removed_elements:
            parts.append(f"Replaces {', '.join(removed_elements)}")

        if replacement_elements:
            parts.append(
                "Introduces replacement element(s): "
                + ", ".join(replacement_elements)
            )

        if candidate.is_stable:
            parts.append("Stable candidate")

        if candidate_risk is None:
            parts.append(
                "Candidate material-risk evidence unavailable; "
                "unknown risk is not treated as low risk"
            )
        elif source_risk is None:
            parts.append(
                f"Candidate material risk is {candidate_risk:.3f}; "
                "source material-risk evidence is unavailable"
            )
        elif candidate_risk < source_risk:
            parts.append(
                f"Lower material risk ({candidate_risk:.3f} vs {source_risk:.3f})"
            )
        elif candidate_risk > source_risk:
            parts.append(
                f"Higher material risk ({candidate_risk:.3f} vs {source_risk:.3f})"
            )
        else:
            parts.append("Similar material risk profile")

        return "; ".join(parts)