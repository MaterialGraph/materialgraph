from fastapi import APIRouter

from app.domain.objective_mode_policy import MODE_POLICIES
from app.schemas.research_objective_exploration import ObjectiveModesResponse

router = APIRouter(prefix="/discovery", tags=["Discovery"])


@router.get(
    "/objective-modes",
    response_model=ObjectiveModesResponse,
    summary="Objective Explore mode policies",
    description=(
        "Returns the executable avoid and prefer policy for each Objective "
        "Explore mode, with descriptions generated from the same policy "
        "objects that drive admission, transition validation, the returned-"
        "chain filter and candidate scoring. Scope: Objective Explore only."
    ),
)
def get_objective_modes():
    return {
        "scope": "objective_explore",
        "modes": [policy.exposed() for policy in MODE_POLICIES.values()],
    }
