from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.comparison import (
    CandidateComparisonRequest,
    CandidateComparisonResult,
    CandidateComparisonUnavailable,
)
from app.services.candidate_comparison_service import CandidateComparisonService

router = APIRouter(prefix="/comparison", tags=["Comparison"])


@router.post(
    "/materials",
    response_model=CandidateComparisonResult,
    summary="Compare candidate materials",
    description=(
        "Compares two candidate materials under selected constraints, "
        "including similarity, risk, and recommendation-relevant signals."
    ),
)
def compare_materials(
    request: CandidateComparisonRequest,
    db: Session = Depends(get_db),
):
    service = CandidateComparisonService(db)
    result = service.compare_candidates(request)

    if isinstance(result, CandidateComparisonUnavailable):
        has_missing_material = any(
            candidate.disposition == "material_not_found"
            for candidate in result.unavailable_candidates
        )
        status_code = 404 if has_missing_material else 422
        raise HTTPException(
            status_code=status_code,
            detail=result.model_dump(),
        )

    return result