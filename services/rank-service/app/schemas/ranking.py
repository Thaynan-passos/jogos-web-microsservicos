from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RankingEntryCreate(BaseModel):
    user_id: UUID | str = Field(default_factory=uuid4)
    username: str = Field(min_length=2, max_length=50)
    game_slug: str = Field(min_length=2, max_length=50)
    score: int = Field(ge=0)
    duration_ms: int = Field(default=0, ge=0)


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
