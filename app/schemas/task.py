"""Схемы Pydantic для создания, чтения и частичного обновления задач."""

from pydantic import BaseModel, Field, ConfigDict
from datetime import date

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    # Схема создания намеренно остаётся компактной.
    title: str = Field(min_length=3, max_length=50)
    description: str | None = None
    deadline: date | None = None

class TaskRead(BaseModel):
    # ORM-объекты валидируем через from_attributes для удобной сериализации.
    id: int
    title: str = Field(min_length=3, max_length=50)
    description: str | None
    deadline: date | None
    owner_id: int
    status: TaskStatus

    model_config = ConfigDict(from_attributes=True)

class TaskUpdate(BaseModel):
    # Необязательные поля позволяют патчить только нужные значения.
    title: str | None
    description: str | None = None
    deadline: date | None = None
    status: TaskStatus | None = None
