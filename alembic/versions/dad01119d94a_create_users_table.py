"""Создание таблицы пользователей.

Revision ID: dad01119d94a
Revises:
Create Date: 2026-06-15 12:55:29.923581

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dad01119d94a"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Обновление схемы."""
    # ### Команды, сгенерированные Alembic, при необходимости можно править. ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    # ### Конец команд Alembic ###


def downgrade() -> None:
    """Откат схемы."""
    # ### Команды, сгенерированные Alembic, при необходимости можно править. ###
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    # ### Конец команд Alembic ###
