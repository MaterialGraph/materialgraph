"""Objective Explore mode policy: one executable source per mode (contract P).

Each mode's avoid and prefer behaviour is defined once here. Admission,
transition validation, the returned-chain filter and candidate scoring read
their behaviour and penalty values from these objects, and every description
shown to users (constraint policy, explanations, warnings, mode hints) is
generated from them.

Scope: Objective Explore only (register entry 37, condition d). Discovery
candidates, the Objective Chains API and Scientific Pathway Analysis keep
their own behaviour.

The values encode the behaviour verified at the Release 1 baseline (P-6):
Balanced and Exploratory generate the same chains and differ only in the
candidate-level avoid penalty and Exploratory's absolute score offset; Strict
additionally excludes avoided elements from every non-source material. Strict
reads element records at admission and formula symbols in its final filter;
that split is disclosed here, not changed (P-7).
"""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class AvoidPolicy:
    # A step whose target introduces an avoided element absent from the
    # current material is rejected during transition validation.
    introduced: str
    # Avoided elements already present (for example inherited from the
    # source): allowed with a candidate penalty, or excluded.
    inherited: str
    candidate_penalty: float
    admission: str
    admission_evidence: str | None
    missing_element_records: str | None
    final_filter: str | None
    final_filter_evidence: str | None
    applies_to: str


@dataclass(frozen=True)
class PreferPolicy:
    admission: str
    reservation_order: str
    candidate_bonus_per_element: float


@dataclass(frozen=True)
class ModePolicy:
    mode: str
    label: str
    avoid: AvoidPolicy
    prefer: PreferPolicy
    candidate_score_offset: float

    @property
    def hard_avoid_admission(self) -> bool:
        return self.avoid.admission == "exclude_any_avoided"

    @property
    def objective_aware_prefer_allocation(self) -> bool:
        return self.prefer.admission == "one_reserved_slot_per_element"

    @property
    def reject_introduced_avoided(self) -> bool:
        return self.avoid.introduced == "rejected_at_transition"

    @property
    def applies_final_filter(self) -> bool:
        return self.avoid.final_filter is not None

    def avoid_policy(self) -> dict:
        return asdict(self.avoid)

    def prefer_policy(self) -> dict:
        return asdict(self.prefer)

    def constraint_policy(self) -> dict[str, str]:
        if self.applies_final_filter:
            return {
                "avoid_elements": "exclude_non_source",
                "prefer_elements": "reserved_slot_and_bonus",
                "hard_rejection_scope": "all_non_root_chain_materials",
            }
        return {
            "avoid_elements": "reject_introduced_penalize_inherited",
            "prefer_elements": "reserved_slot_and_bonus",
            "hard_rejection_scope": "none",
        }

    def avoid_explanation(self) -> str:
        """Backend explanation of Avoid for this mode (objective coverage)."""
        if self.applies_final_filter:
            return (
                f"{self.label} mode excludes materials containing avoided "
                "elements during search, using recorded element membership; "
                "materials without membership records are also excluded. It "
                "then removes returned chains in which any material other "
                "than the source contains an avoided element, read from "
                "formula symbols. The source material is exempt."
            )
        return (
            f"{self.label} mode does not explore steps that would introduce "
            "an avoided element. Avoided elements already present, for "
            "example inherited from the source, are allowed and lower a "
            f"material's objective score by {_points(self.avoid.candidate_penalty)}, "
            "so returned materials or chains may still contain them."
        )

    def prefer_explanation(self) -> str:
        return (
            "Each preferred element reserves one exploration slot per "
            f"expansion ({self.prefer.reservation_order} order when slots "
            "run short) and adds "
            f"{_points(self.prefer.candidate_bonus_per_element)} to a "
            "material's objective score."
        )

    def description(self) -> str:
        """Mode hint shown before a request is made."""
        text = f"{self.avoid_explanation()} {self.prefer_explanation()}"
        if self.candidate_score_offset:
            text += (
                f" Every ranked material also receives a fixed "
                f"{_points(self.candidate_score_offset)} offset, which does "
                "not change their order."
            )
        return text

    def warning(self) -> str:
        if self.applies_final_filter:
            return (
                f"{self.label} mode applies explicit hard constraints and may "
                "exclude scientifically interesting candidates."
            )
        if self.candidate_score_offset:
            return (
                f"{self.label} mode explores the same candidates as Balanced; "
                "it differs only in a smaller penalty for avoided elements "
                "already present and a fixed score offset."
            )
        return (
            f"{self.label} mode ranks and warns; it does not explore steps "
            "that introduce an avoided element, and keeps materials whose "
            "avoided elements are already present, with a penalty."
        )

    def exposed(self) -> dict:
        """Structured policy as served to clients."""
        return {
            "mode": self.mode,
            "label": self.label,
            "avoid_policy": self.avoid_policy(),
            "prefer_policy": self.prefer_policy(),
            "candidate_score_offset": self.candidate_score_offset,
            "constraint_policy": self.constraint_policy(),
            "description": self.description(),
            "avoid_policy_explanation": self.avoid_explanation(),
            "warning": self.warning(),
        }


def _points(value: float) -> str:
    number = int(value) if float(value).is_integer() else value
    return f"{number} point{'s' if number != 1 else ''}"


_PREFER = PreferPolicy(
    admission="one_reserved_slot_per_element",
    reservation_order="alphabetical",
    candidate_bonus_per_element=15.0,
)

MODE_POLICIES: dict[str, ModePolicy] = {
    "balanced": ModePolicy(
        mode="balanced",
        label="Balanced",
        avoid=AvoidPolicy(
            introduced="rejected_at_transition",
            inherited="allowed_with_penalty",
            candidate_penalty=25.0,
            admission="not_used",
            admission_evidence=None,
            missing_element_records=None,
            final_filter=None,
            final_filter_evidence=None,
            applies_to="non_source",
        ),
        prefer=_PREFER,
        candidate_score_offset=0.0,
    ),
    "exploratory": ModePolicy(
        mode="exploratory",
        label="Exploratory",
        avoid=AvoidPolicy(
            introduced="rejected_at_transition",
            inherited="allowed_with_penalty",
            candidate_penalty=10.0,
            admission="not_used",
            admission_evidence=None,
            missing_element_records=None,
            final_filter=None,
            final_filter_evidence=None,
            applies_to="non_source",
        ),
        prefer=_PREFER,
        candidate_score_offset=5.0,
    ),
    "strict": ModePolicy(
        mode="strict",
        label="Strict",
        avoid=AvoidPolicy(
            introduced="rejected_at_transition",
            inherited="excluded_non_source",
            # Still applied to candidate scores, as at the baseline.
            candidate_penalty=25.0,
            admission="exclude_any_avoided",
            admission_evidence="element_records",
            missing_element_records="excluded",
            final_filter="exclude_chains_with_avoided_non_source",
            final_filter_evidence="formula_symbols",
            applies_to="non_source",
        ),
        prefer=_PREFER,
        candidate_score_offset=0.0,
    ),
}


def mode_policy(mode: str) -> ModePolicy:
    return MODE_POLICIES[mode]
