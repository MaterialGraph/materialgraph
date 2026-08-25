"""add material element fraction evidence

Revision ID: 7a4c2e91b6d8
Revises: f1a8b10be960
Create Date: 2026-08-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7a4c2e91b6d8"
down_revision: Union[str, Sequence[str], None] = "f1a8b10be960"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "material_elements",
        sa.Column(
            "fraction_known",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("material_elements", "fraction_known")