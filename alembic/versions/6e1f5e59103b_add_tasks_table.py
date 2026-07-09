"""Создание таблицы задач.

Revision ID: 6e1f5e59103b
Revises: fb1ee122ccbe
Create Date: 2026-06-16 17:49:54.259236

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "6e1f5e59103b"
down_revision: Union[str, Sequence[str], None] = "fb1ee122ccbe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Обновление схемы."""
    # ### Команды, сгенерированные Alembic, при необходимости можно править. ###
    pass
    # ### Конец команд Alembic ###


def downgrade() -> None:
    """Откат схемы."""
    # ### Команды, сгенерированные Alembic, при необходимости можно править. ###
    pass
    # ### Конец команд Alembic ###
