"""Создание таблицы задач.

Revision ID: fb1ee122ccbe
Revises: dad01119d94a
Create Date: 2026-06-15 22:38:08.155343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb1ee122ccbe'
down_revision: Union[str, Sequence[str], None] = 'dad01119d94a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Обновление схемы."""
    # ### Команды, сгенерированные Alembic, при необходимости можно править. ###
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('deadline', sa.DateTime(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_owner_id'), 'tasks', ['owner_id'], unique=False)
    # ### Конец команд Alembic ###


def downgrade() -> None:
    """Откат схемы."""
    # ### Команды, сгенерированные Alembic, при необходимости можно править. ###
    op.drop_index(op.f('ix_tasks_owner_id'), table_name='tasks')
    op.drop_table('tasks')
    # ### Конец команд Alembic ###
