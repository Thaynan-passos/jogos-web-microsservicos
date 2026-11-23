from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GameCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=50, pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=500)
    enabled: bool = True


class GameUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    enabled: bool | None = None

    @field_validator("name", "description", "enabled")
    @classmethod
    def update_values_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("Este campo não pode ser nulo")
        return value


class GameResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    name: str
    description: str
    enabled: bool
    created_at: datetime
