from pydantic import BaseModel, Field, ConfigDict
from datetime import date

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str | None = None
    deadline: date | None = None

class TaskRead(BaseModel):
    id: int
    title: str = Field(min_length=3, max_length=50)
    description: str | None
    deadline: date | None
    owner_id: int
    status: TaskStatus

    model_config = ConfigDict(from_attributes=True)

class TaskUpdate(BaseModel):
    title: str | None
    description: str | None = None
    deadline: date | None = None
    status: TaskStatus | None = None