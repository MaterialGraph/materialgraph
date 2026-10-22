from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.material import Material
from app.schemas.material import MaterialDetail, MaterialRead
from app.schemas.material_search import MaterialSearchResponse, SearchMode
from app.services.material.query_service import MaterialQueryService
from app.services.material.search_service import (
    MaterialSearchService,
    SearchQueryError,
)

router = APIRouter(prefix="/materials", tags=["Materials"])


@router.get(
    "",
    response_model=list[MaterialRead],
    summary="List materials",
    description="Returns materials ordered by internal ID.",
)
def list_materials(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return (
        db.query(Material)
        .order_by(Material.id)
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get(
    "/search",
    response_model=MaterialSearchResponse,
    summary="Search the full dataset",
    description=(
        "Searches every material in the dataset, not only loaded rows. The "
        "mode is explicit: formula (composition equality within 1e-6 on "
        "normalised fractions), mp_id (exact), chemsys (exact element set) "
        "or contains (supersets). Element symbols are case-sensitive. "
        "Invalid input returns 422 with an explanation; it is never "
        "corrected or reinterpreted."
    ),
)
def search_materials(
    mode: SearchMode = Query(...),
    q: str = Query(...),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    try:
        return MaterialSearchService(db).search(
            mode=mode,
            query=q,
            limit=limit,
            offset=offset,
        )
    except SearchQueryError as error:
        raise HTTPException(status_code=422, detail=error.detail()) from error


@router.get("/{material_id}", response_model=MaterialRead)
def get_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()

    if material is None:
        raise HTTPException(status_code=404, detail="Material not found")

    return material

@router.get("/{material_id}/detail", response_model=MaterialDetail)
def get_material_detail(
    material_id: int,
    db: Session = Depends(get_db),
):
    service = MaterialQueryService(db)
    result = service.get_material_with_elements(material_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Material not found")

    material, elements = result

    return MaterialDetail.model_validate(
        {
            **material.__dict__,
            "elements": elements,
        }
    )