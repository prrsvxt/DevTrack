from sqlalchemy import String, Text, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='cascade'), nullable=False, index=True)
    owner: Mapped['User'] = relationship(back_populates='tasks')