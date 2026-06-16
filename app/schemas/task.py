from pydantic import BaseModel, Field
from datetime import datetime


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str | None = None
    deadline: datetime | None = None

class TaskRead(BaseModel):
    id: int
    title: str = Field(min_length=3, max_length=50)
    description: str | None
    deadline: datetime | None
    owner_id: int

class TaskUpdate(BaseModel):
    title: str | None
    description: str | None = None
    deadline: datetime | None = None