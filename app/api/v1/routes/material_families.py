from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.material_family import MaterialFamiliesResponse
from app.services.material.family_service import MaterialFamilyService

from app.api.v1.route_utils import ensure_material_found

router = APIRouter(
    prefix="/materials",
    tags=["Material Families"],
)


@router.get(
    "/{material_id}/families",
    response_model=MaterialFamiliesResponse,
    summary="Get material families",
    description=(
        "Returns composition-heuristic related-material candidates based on shared "
        "chemistry, alkali-substitution hypotheses, transition-metal similarity, "
        "phosphate-related elemental chemistry, and oxide chemistry. These labels "
        "do not validate structural family membership or substitution mechanisms."
    ),
)
def get_material_families(
    material_id: int,
    db: Session = Depends(get_db),
) -> MaterialFamiliesResponse:
    service = MaterialFamilyService(db)

    result = service.get_material_families(material_id)

    ensure_material_found(result)

    return result