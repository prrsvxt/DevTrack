"""Добавление статуса задачи.

Revision ID: 8c97d09ecf38
Revises: 6e1f5e59103b
Create Date: 2026-06-16 21:34:25.319403

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8c97d09ecf38"
down_revision: Union[str, Sequence[str], None] = "6e1f5e59103b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Обновление схемы."""
    # ### Команды, сгенерированные Alembic, при необходимости можно править. ###

    task_status_enum = sa.Enum(
        "NEW",
        "IN_PROGRESS",
        "DONE",
        name="taskstatus",
    )

    task_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "tasks",
        sa.Column("status", task_status_enum, nullable=False, server_default="NEW"),
    )
    # ### Конец команд Alembic ###


def downgrade() -> None:
    """Откат схемы."""
    # ### Команды, сгенерированные Alembic, при необходимости можно править. ###
    op.drop_column("tasks", "status")
    # ### Конец команд Alembic ###
