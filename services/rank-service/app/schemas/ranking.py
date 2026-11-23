from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class RankingEntryCreate(BaseModel):
    user_id: UUID | None = None
    username: str = Field(min_length=2, max_length=50)
    game_slug: str = Field(min_length=2, max_length=50)
    score: int = Field(ge=0)
    duration_ms: int = Field(default=0, ge=0)


class RankingEntryUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=2, max_length=50)
    game_slug: str | None = Field(default=None, min_length=2, max_length=50)
    score: int | None = Field(default=None, ge=0)
    duration_ms: int | None = Field(default=None, ge=0)
    matches_played: int | None = Field(default=None, ge=1)
    win_rate: str | None = Field(default=None, min_length=1, max_length=10)

    @field_validator(
        "username",
        "game_slug",
        "score",
        "duration_ms",
        "matches_played",
        "win_rate",
    )
    @classmethod
    def update_values_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("Este campo não pode ser nulo")
        return value


class RankingEntryResponse(BaseModel):
    id: str
    position: int
    user_id: str
    username: str
    game_slug: str
    game_name: str
    score: int
    duration_ms: int
    duration_formatted: str
    achieved_at: datetime
    matches_played: int
    win_rate: str


class RankingSummary(BaseModel):
    total_entries: int
    top_players: list[RankingEntryResponse]
    most_popular_game: str
    highest_score: int
