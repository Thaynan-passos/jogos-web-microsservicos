import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class SessionCreate(BaseModel):
    game_slug: str = Field(min_length=1, max_length=50)
    user_id: uuid.UUID | None = None


class SessionResult(BaseModel):
    result: dict[str, Any] = Field(default_factory=dict)


class SessionUpdate(BaseModel):
    status: Literal["in_progress", "completed", "abandoned"] | None = None
    result: dict[str, Any] | None = None

    @field_validator("status", "result")
    @classmethod
    def update_values_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("Este campo não pode ser nulo")
        return value


class SessionResponse(BaseModel):
    id: uuid.UUID
    game_slug: str
    user_id: uuid.UUID | None
    status: Literal["in_progress", "completed", "abandoned"]
    result: dict[str, Any]
    started_at: datetime
    completed_at: datetime | None
