from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Query, status

from app.schemas.ranking import (
    RankingEntryCreate,
    RankingEntryResponse,
    RankingSummary,
)

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
INITIAL_ENTRIES = [
    {
        "id": "e1-velha-1",
        "user_id": str(uuid.uuid4()),
        "username": "LucasMestre",
        "game_slug": "tic-tac-toe",
        "score": 450,
        "duration_ms": 42000,
        "achieved_at": datetime(2026, 10, 29, 14, 20, tzinfo=timezone.utc),
        "matches_played": 18,
        "win_rate": "89%",
    },
    {
        "id": "e2-memoria-1",
        "user_id": str(uuid.uuid4()),
        "username": "AnaMemoryQueen",
        "game_slug": "memory",
        "score": 820,
        "duration_ms": 28500,
        "achieved_at": datetime(2026, 10, 29, 17, 10, tzinfo=timezone.utc),
        "matches_played": 24,
        "win_rate": "95%",
    },
    {
        "id": "e3-rps-1",
        "user_id": str(uuid.uuid4()),
        "username": "GabrielTactics",
        "game_slug": "rps",
        "score": 380,
        "duration_ms": 35000,
        "achieved_at": datetime(2026, 10, 30, 9, 45, tzinfo=timezone.utc),
        "matches_played": 15,
        "win_rate": "80%",
    },
    {
        "id": "e4-velha-2",
        "user_id": str(uuid.uuid4()),
        "username": "Beatriz_Gamer",
        "game_slug": "tic-tac-toe",
        "score": 390,
        "duration_ms": 48000,
        "achieved_at": datetime(2026, 10, 30, 11, 15, tzinfo=timezone.utc),
        "matches_played": 14,
        "win_rate": "78%",
    },
    {
        "id": "e5-memoria-2",
        "user_id": str(uuid.uuid4()),
        "username": "DiegoCards",
        "game_slug": "memory",
        "score": 690,
        "duration_ms": 34000,
        "achieved_at": datetime(2026, 10, 30, 12, 30, tzinfo=timezone.utc),
        "matches_played": 19,
        "win_rate": "84%",
    },
    {
        "id": "e6-rps-2",
        "user_id": str(uuid.uuid4()),
        "username": "Mariana_RPS",
        "game_slug": "rps",
        "score": 340,
        "duration_ms": 40000,
        "achieved_at": datetime(2026, 10, 30, 13, 0, tzinfo=timezone.utc),
        "matches_played": 12,
        "win_rate": "75%",
    },
]

# Estado em memória compartilhada no processo
ranking_store: list[dict] = list(INITIAL_ENTRIES)


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
        entries = [
            e for e in entries if normalize_slug(e["game_slug"]) == norm_slug
        ]

    # Ordena por pontuação descrescente e menor duração
    sorted_entries = sorted(
        entries,
        key=lambda x: (-x["score"], x.get("duration_ms", 999999)),
    )

    result: list[RankingEntryResponse] = []
    for pos, item in enumerate(sorted_entries[:limit], start=1):
        slug = item["game_slug"]
        game_title = GAME_NAMES.get(slug, slug.replace("-", " ").title())
        result.append(
            RankingEntryResponse(
                id=str(item["id"]),
                position=pos,
                user_id=str(item["user_id"]),
                username=item["username"],
                game_slug=slug,
                game_name=game_title,
                score=item["score"],
                duration_ms=item.get("duration_ms", 0),
                duration_formatted=format_duration(item.get("duration_ms", 0)),
                achieved_at=item.get("achieved_at", datetime.now(timezone.utc)),
                matches_played=item.get("matches_played", 1),
                win_rate=item.get("win_rate", "100%"),
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
            if e["username"].lower() == payload.username.lower()
            and normalize_slug(e["game_slug"]) == norm_slug
        ),
        None,
    )

    if existing:
        existing["matches_played"] = existing.get("matches_played", 1) + 1
        if payload.score > existing["score"]:
            existing["score"] = payload.score
            existing["duration_ms"] = payload.duration_ms
            existing["achieved_at"] = datetime.now(timezone.utc)
        target_entry = existing
    else:
        new_entry = {
            "id": entry_id,
            "user_id": str(payload.user_id),
            "username": payload.username,
            "game_slug": payload.game_slug,
            "score": payload.score,
            "duration_ms": payload.duration_ms,
            "achieved_at": datetime.now(timezone.utc),
            "matches_played": 1,
            "win_rate": "100%",
        }
        ranking_store.append(new_entry)
        target_entry = new_entry

    # Calcula posição no jogo
    same_game_sorted = sorted(
        [
            e
            for e in ranking_store
            if normalize_slug(e["game_slug"]) == norm_slug
        ],
        key=lambda x: (-x["score"], x.get("duration_ms", 999999)),
    )
    pos = 1
    for index, item in enumerate(same_game_sorted, start=1):
        if item["id"] == target_entry["id"]:
            pos = index
            break

    slug = target_entry["game_slug"]
    return RankingEntryResponse(
        id=str(target_entry["id"]),
        position=pos,
        user_id=str(target_entry["user_id"]),
        username=target_entry["username"],
        game_slug=slug,
        game_name=GAME_NAMES.get(slug, slug.replace("-", " ").title()),
        score=target_entry["score"],
        duration_ms=target_entry.get("duration_ms", 0),
        duration_formatted=format_duration(target_entry.get("duration_ms", 0)),
        achieved_at=target_entry.get("achieved_at", datetime.now(timezone.utc)),
        matches_played=target_entry.get("matches_played", 1),
        win_rate=target_entry.get("win_rate", "100%"),
    )


@router.get("/summary", response_model=RankingSummary)
async def get_ranking_summary() -> RankingSummary:
    sorted_all = sorted(ranking_store, key=lambda x: -x["score"])
    top_3: list[RankingEntryResponse] = []
    for pos, item in enumerate(sorted_all[:3], start=1):
        slug = item["game_slug"]
        top_3.append(
            RankingEntryResponse(
                id=str(item["id"]),
                position=pos,
                user_id=str(item["user_id"]),
                username=item["username"],
                game_slug=slug,
                game_name=GAME_NAMES.get(slug, slug.replace("-", " ").title()),
                score=item["score"],
                duration_ms=item.get("duration_ms", 0),
                duration_formatted=format_duration(item.get("duration_ms", 0)),
                achieved_at=item.get("achieved_at", datetime.now(timezone.utc)),
                matches_played=item.get("matches_played", 1),
                win_rate=item.get("win_rate", "100%"),
            )
        )

    highest = sorted_all[0]["score"] if sorted_all else 0
    return RankingSummary(
        total_entries=len(ranking_store),
        top_players=top_3,
        most_popular_game="Jogo da Memória",
        highest_score=highest,
    )
