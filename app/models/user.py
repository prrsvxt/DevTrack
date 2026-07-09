"""SQLAlchemy-модель, описывающая пользователей приложения."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.team_member import TeamMember


class User(Base):
    # Явно задаём имя таблицы, чтобы миграции и запросы были предсказуемыми.
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    tasks: Mapped[list["Task"]] = relationship(back_populates="owner")
    team_members: Mapped[list["TeamMember"]] = relationship(back_populates="user")
