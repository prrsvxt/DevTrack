"""Изменение типа deadline с DateTime на Date в задачах.

Revision ID: bf42373bcd3a
Revises: 8c97d09ecf38
Create Date: 2026-06-17 13:38:26.999282

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "bf42373bcd3a"
down_revision: Union[str, Sequence[str], None] = "8c97d09ecf38"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Обновление схемы."""
    # ### Команды, сгенерированные Alembic, при необходимости можно править. ###
    op.alter_column(
        "tasks",
        "deadline",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.Date(),
        existing_nullable=True,
    )
    # ### Конец команд Alembic ###


def downgrade() -> None:
    """Откат схемы."""
    # ### Команды, сгенерированные Alembic, при необходимости можно править. ###
    op.alter_column(
        "tasks",
        "deadline",
        existing_type=sa.Date(),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
    )
    # ### Конец команд Alembic ###
