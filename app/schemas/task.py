"""Схемы Pydantic для создания, чтения и частичного обновления задач."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    # Схема создания остаётся компактной, но поддерживает привязку к команде.
    title: str = Field(min_length=3, max_length=50)
    description: str | None = None
    deadline: date | None = None
    team_id: int | None = None


class TaskRead(BaseModel):
    # ORM-объекты валидируем через from_attributes для удобной сериализации.
    id: int
    title: str = Field(min_length=3, max_length=50)
    description: str | None
    deadline: date | None
    owner_id: int
    team_id: int | None
    status: TaskStatus

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    # Частичное обновление оставляем без team_id, чтобы не размывать владение задачей.
    title: str | None = None
    description: str | None = None
    deadline: date | None = None
    status: TaskStatus | None = None
