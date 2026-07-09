from pydantic import BaseModel
from datetime import datetime
from pydantic import ConfigDict


class CreateTeam(BaseModel):
    name: str
    description: str | None = None


class UpdateTeam(BaseModel):
    name: str | None = None
    description: str | None = None


class TeamResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
