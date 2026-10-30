import uuid
from datetime import UTC, datetime

from app.schemas.ranking import (
    RankingEntryCreate,
    RankingEntryResponse,
    RankingSummary,
)
from fastapi import APIRouter, Query, status
from pydantic import BaseModel


class RankingStoreEntry(BaseModel):
    id: str
    user_id: str
    username: str
    game_slug: str
    score: int
    duration_ms: int
    achieved_at: datetime
    matches_played: int = 1
    win_rate: str = "100%"


router = APIRouter(prefix="/rankings", tags=["rankings"])

GAME_NAMES = {
    "tic-tac-toe": "Jogo da Velha",
    "jogo-da-velha": "Jogo da Velha",
    "memory": "Jogo da Memória",
    "jogo-da-memoria": "Jogo da Memória",
    "rps": "Pedra, Papel e Tesoura",
    "pedra-papel-tesoura": "Pedra, Papel e Tesoura",
}

# Base inicial com dados de exemplo realistas para demonstração e desenvolvimento
INITIAL_ENTRIES: list[RankingStoreEntry] = [
    RankingStoreEntry(
        id="e1-velha-1",
        user_id=str(uuid.uuid4()),
        username="LucasMestre",
        game_slug="tic-tac-toe",
        score=450,
        duration_ms=42000,
        achieved_at=datetime(2026, 10, 29, 14, 20, tzinfo=UTC),
        matches_played=18,
        win_rate="89%",
    ),
    RankingStoreEntry(
        id="e2-memoria-1",
        user_id=str(uuid.uuid4()),
        username="AnaMemoryQueen",
        game_slug="memory",
        score=820,
        duration_ms=28500,
        achieved_at=datetime(2026, 10, 29, 17, 10, tzinfo=UTC),
        matches_played=24,
        win_rate="95%",
    ),
    RankingStoreEntry(
        id="e3-rps-1",
        user_id=str(uuid.uuid4()),
        username="GabrielTactics",
        game_slug="rps",
        score=380,
        duration_ms=35000,
        achieved_at=datetime(2026, 10, 30, 9, 45, tzinfo=UTC),
        matches_played=15,
        win_rate="80%",
    ),
    RankingStoreEntry(
        id="e4-velha-2",
        user_id=str(uuid.uuid4()),
        username="Beatriz_Gamer",
        game_slug="tic-tac-toe",
        score=390,
        duration_ms=48000,
        achieved_at=datetime(2026, 10, 30, 11, 15, tzinfo=UTC),
        matches_played=14,
        win_rate="78%",
    ),
    RankingStoreEntry(
        id="e5-memoria-2",
        user_id=str(uuid.uuid4()),
        username="DiegoCards",
        game_slug="memory",
        score=690,
        duration_ms=34000,
        achieved_at=datetime(2026, 10, 30, 12, 30, tzinfo=UTC),
        matches_played=19,
        win_rate="84%",
    ),
    RankingStoreEntry(
        id="e6-rps-2",
        user_id=str(uuid.uuid4()),
        username="Mariana_RPS",
        game_slug="rps",
        score=340,
        duration_ms=40000,
        achieved_at=datetime(2026, 10, 30, 13, 0, tzinfo=UTC),
        matches_played=12,
        win_rate="75%",
    ),
]


# Estado em memória compartilhada no processo
ranking_store: list[RankingStoreEntry] = list(INITIAL_ENTRIES)


def format_duration(ms: int) -> str:
    seconds = max(0, ms // 1000)
    minutes = seconds // 60
    rem_seconds = seconds % 60
    if minutes > 0:
        return f"{minutes}m {rem_seconds:02d}s"
    return f"{rem_seconds}s"


def normalize_slug(slug: str) -> str:
    mapping = {
        "jogo-da-velha": "tic-tac-toe",
        "jogo-da-memoria": "memory",
        "pedra-papel-tesoura": "rps",
    }
    return mapping.get(slug, slug)


@router.get("/", response_model=list[RankingEntryResponse])
async def list_rankings(
    game_slug: str | None = Query(None, description="Filtrar por jogo específico"),
    limit: int = Query(50, ge=1, le=100),
) -> list[RankingEntryResponse]:

    entries = ranking_store

    if game_slug and game_slug != "all":
        norm_slug = normalize_slug(game_slug)
        entries = [e for e in entries if normalize_slug(e.game_slug) == norm_slug]

    sorted_entries = sorted(
        entries,
        key=lambda x: (-x.score, x.duration_ms),
    )

    result = []

    for pos, item in enumerate(sorted_entries[:limit], start=1):
        slug = item.game_slug

        result.append(
            RankingEntryResponse(
                id=item.id,
                position=pos,
                user_id=item.user_id,
                username=item.username,
                game_slug=slug,
                game_name=GAME_NAMES.get(
                    slug,
                    slug.replace("-", " ").title(),
                ),
                score=item.score,
                duration_ms=item.duration_ms,
                duration_formatted=format_duration(item.duration_ms),
                achieved_at=item.achieved_at,
                matches_played=item.matches_played,
                win_rate=item.win_rate,
            )
        )

    return result


@router.post(
    "/",
    response_model=RankingEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nova pontuação",
)
async def create_ranking_entry(payload: RankingEntryCreate) -> RankingEntryResponse:
    entry_id = str(uuid.uuid4())
    norm_slug = normalize_slug(payload.game_slug)

    # Verifica se o usuário já tem registro nesse jogo para atualizar ou adicionar
    existing = next(
        (
            e
            for e in ranking_store
            if e.username.lower() == payload.username.lower()
            and normalize_slug(e.game_slug) == norm_slug
        ),
        None,
    )

    if existing:
        existing.matches_played += 1
        if payload.score > existing.score:
            existing.score = payload.score
            existing.duration_ms = payload.duration_ms
            existing.achieved_at = datetime.now(UTC)
        target_entry = existing
    else:
        new_entry = RankingStoreEntry(
            id=entry_id,
            user_id=str(payload.user_id),
            username=payload.username,
            game_slug=payload.game_slug,
            score=payload.score,
            duration_ms=payload.duration_ms,
            achieved_at=datetime.now(UTC),
            matches_played=1,
            win_rate="100%",
        )
        ranking_store.append(new_entry)
        target_entry = new_entry

    # Calcula posição no jogo
    same_game_sorted = sorted(
        [e for e in ranking_store if normalize_slug(e.game_slug) == norm_slug],
        key=lambda x: (-x.score, x.duration_ms),
    )

    pos = next(
        (
            index
            for index, item in enumerate(same_game_sorted, start=1)
            if item.id == target_entry.id
        ),
        1,
    )

    return RankingEntryResponse(
        id=target_entry.id,
        position=pos,
        user_id=target_entry.user_id,
        username=target_entry.username,
        game_slug=target_entry.game_slug,
        game_name=GAME_NAMES.get(
            target_entry.game_slug,
            target_entry.game_slug.replace("-", " ").title(),
        ),
        score=target_entry.score,
        duration_ms=target_entry.duration_ms,
        duration_formatted=format_duration(target_entry.duration_ms),
        achieved_at=target_entry.achieved_at,
        matches_played=target_entry.matches_played,
        win_rate=target_entry.win_rate,
    )


@router.get("/summary", response_model=RankingSummary)
async def get_ranking_summary() -> RankingSummary:

    sorted_all = sorted(
        ranking_store,
        key=lambda x: -x.score,
    )

    top_3: list[RankingEntryResponse] = []

    for pos, item in enumerate(sorted_all[:3], start=1):
        slug = item.game_slug

        top_3.append(
            RankingEntryResponse(
                id=item.id,
                position=pos,
                user_id=item.user_id,
                username=item.username,
                game_slug=slug,
                game_name=GAME_NAMES.get(
                    slug,
                    slug.replace("-", " ").title(),
                ),
                score=item.score,
                duration_ms=item.duration_ms,
                duration_formatted=format_duration(item.duration_ms),
                achieved_at=item.achieved_at,
                matches_played=item.matches_played,
                win_rate=item.win_rate,
            )
        )

    highest = sorted_all[0].score if sorted_all else 0

    return RankingSummary(
        total_entries=len(ranking_store),
        top_players=top_3,
        most_popular_game="Jogo da Memória",
        highest_score=highest,
    )
