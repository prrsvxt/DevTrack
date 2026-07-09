"""Добавление привязки задач к командам.

Revision ID: e5c0f44d9b91
Revises: bf42373bcd3a
Create Date: 2026-07-09 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e5c0f44d9b91"
down_revision: Union[str, Sequence[str], None] = "bf42373bcd3a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Обновление схемы."""
    op.add_column("tasks", sa.Column("team_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_tasks_team_id"), "tasks", ["team_id"], unique=False)
    op.create_foreign_key(
        "fk_tasks_team_id_teams",
        "tasks",
        "teams",
        ["team_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Откат схемы."""
    op.drop_constraint("fk_tasks_team_id_teams", "tasks", type_="foreignkey")
    op.drop_index(op.f("ix_tasks_team_id"), table_name="tasks")
    op.drop_column("tasks", "team_id")
