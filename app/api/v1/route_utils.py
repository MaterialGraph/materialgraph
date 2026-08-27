from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.material import Material


def ensure_material_exists(db: Session, material_id: int) -> None:
    if db.get(Material, material_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Material not found",
        )


def ensure_material_found(result: dict) -> None:
    if result.get("mp_id") is None:
        raise HTTPException(
            status_code=404,
            detail="Material not found",
        )
