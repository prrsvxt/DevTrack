from pydantic import BaseModel
from datetime import datetime


class UpdateTeam(BaseModel):
    name: str | None = None
    description: str | None = None
    owner_id: int
    updated_at: datetime = datetime.now()