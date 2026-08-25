from sqlalchemy import Boolean, Float, ForeignKey, UniqueConstraint, false
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MaterialElement(Base):
    __tablename__ = "material_elements"

    id: Mapped[int] = mapped_column(primary_key=True)

    material_id: Mapped[int] = mapped_column(
        ForeignKey("materials.id", ondelete="CASCADE"),
        index=True,
    )
    element_id: Mapped[int] = mapped_column(
        ForeignKey("elements.id", ondelete="CASCADE"),
        index=True,
    )

    fraction: Mapped[float] = mapped_column(Float)
    fraction_known: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=false(),
    )

    __table_args__ = (
        UniqueConstraint("material_id", "element_id", name="uq_material_element"),
    )