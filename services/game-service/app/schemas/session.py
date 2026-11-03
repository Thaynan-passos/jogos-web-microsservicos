import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    game_slug: str = Field(min_length=1, max_length=50)
    user_id: uuid.UUID | None = None


class SessionResult(BaseModel):
    result: dict[str, Any] = Field(default_factory=dict)


class SessionUpdate(BaseModel):
    status: Literal["in_progress", "completed", "abandoned"] | None = None
    result: dict[str, Any] | None = None


class SessionResponse(BaseModel):
    id: uuid.UUID
    game_slug: str
    user_id: uuid.UUID | None
    status: Literal["in_progress", "completed", "abandoned"]
    result: dict[str, Any]
    started_at: datetime
    completed_at: datetime | None
