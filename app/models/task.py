"""SQLAlchemy-модель задач и enum статусов."""

import enum
from sqlalchemy import String, Text, Date, ForeignKey, Enum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TaskStatus(enum.Enum):
    # Значения статусов держим короткими для API и хранения в БД.
    NEW = 'new'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


class Task(Base):
    # Задачи принадлежат пользователям и удаляются каскадно вместе с ними.
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(Date(), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='cascade'), nullable=False, index=True)
    owner: Mapped['User'] = relationship(back_populates='tasks')
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.NEW, nullable=False)
