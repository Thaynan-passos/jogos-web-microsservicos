from datetime import UTC, datetime
from uuid import UUID

from app.db.session import get_db
from app.models.ranking import RankingEntry
from app.schemas.ranking import (
    RankingEntryCreate,
    RankingEntryResponse,
    RankingEntryUpdate,
    RankingSummary,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/rankings", tags=["rankings"])

GAME_NAMES = {
    "tic-tac-toe": "Jogo da Velha",
    "jogo-da-velha": "Jogo da Velha",
    "memory": "Jogo da Memória",
    "jogo-da-memoria": "Jogo da Memória",
    "rps": "Pedra, Papel e Tesoura",
    "pedra-papel-tesoura": "Pedra, Papel e Tesoura",
}


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
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> list[RankingEntryResponse]:
    query = select(RankingEntry)
    if game_slug and game_slug != "all":
        query = query.where(RankingEntry.game_slug == normalize_slug(game_slug))
    query = query.order_by(RankingEntry.score.desc(), RankingEntry.duration_ms).limit(
        limit
    )
    entries = (await db.scalars(query)).all()
    return [
        to_response(item, position) for position, item in enumerate(entries, start=1)
    ]


def to_response(item: RankingEntry, position: int) -> RankingEntryResponse:
    return RankingEntryResponse(
        id=str(item.id),
        position=position,
        user_id=str(item.user_id),
        username=item.username,
        game_slug=item.game_slug,
        game_name=GAME_NAMES.get(
            item.game_slug, item.game_slug.replace("-", " ").title()
        ),
        score=item.score,
        duration_ms=item.duration_ms,
        duration_formatted=format_duration(item.duration_ms),
        achieved_at=item.achieved_at,
        matches_played=item.matches_played,
        win_rate=item.win_rate,
    )


@router.post(
    "/",
    response_model=RankingEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nova pontuação",
)
async def create_ranking_entry(
    payload: RankingEntryCreate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> RankingEntryResponse:
    norm_slug = normalize_slug(payload.game_slug)
    existing = await db.scalar(
        select(RankingEntry).where(
            func.lower(RankingEntry.username) == payload.username.lower(),
            RankingEntry.game_slug == norm_slug,
        )
    )

    if existing:
        existing.matches_played += 1
        if payload.score > existing.score:
            existing.score = payload.score
            existing.duration_ms = payload.duration_ms
            existing.achieved_at = datetime.now(UTC)
        target_entry = existing
    else:
        target_entry = RankingEntry(
            user_id=payload.user_id,
            username=payload.username,
            game_slug=norm_slug,
            score=payload.score,
            duration_ms=payload.duration_ms,
            matches_played=1,
            win_rate="100%",
        )
        db.add(target_entry)

    await db.commit()
    await db.refresh(target_entry)

    position_query = (
        select(func.count())
        .select_from(RankingEntry)
        .where(
            RankingEntry.game_slug == norm_slug,
            (RankingEntry.score > target_entry.score)
            | (
                (RankingEntry.score == target_entry.score)
                & (RankingEntry.duration_ms < target_entry.duration_ms)
            ),
        )
    )
    position = (await db.scalar(position_query) or 0) + 1
    return to_response(target_entry, position)


@router.get("/summary", response_model=RankingSummary)
async def get_ranking_summary(db: AsyncSession = Depends(get_db)) -> RankingSummary:  # noqa: B008
    sorted_entries = (
        await db.scalars(
            select(RankingEntry).order_by(RankingEntry.score.desc()).limit(3)
        )
    ).all()
    total = await db.scalar(select(func.count()).select_from(RankingEntry)) or 0
    highest = await db.scalar(select(func.max(RankingEntry.score))) or 0
    popular_game_slug = await db.scalar(
        select(RankingEntry.game_slug)
        .group_by(RankingEntry.game_slug)
        .order_by(func.count().desc())
        .limit(1)
    )
    top_3 = [
        to_response(item, position)
        for position, item in enumerate(sorted_entries, start=1)
    ]

    return RankingSummary(
        total_entries=total,
        top_players=top_3,
        most_popular_game=(
            GAME_NAMES.get(popular_game_slug, popular_game_slug)
            if popular_game_slug
            else "Nenhum jogo"
        ),
        highest_score=highest,
    )


@router.get("/{entry_id}", response_model=RankingEntryResponse)
async def get_ranking_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> RankingEntryResponse:
    entry = await db.get(RankingEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Pontuação não encontrada")
    position = await ranking_position(entry, db)
    return to_response(entry, position)


@router.put("/{entry_id}", response_model=RankingEntryResponse)
async def update_ranking_entry(
    entry_id: UUID,
    payload: RankingEntryUpdate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> RankingEntryResponse:
    entry = await db.get(RankingEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Pontuação não encontrada")
    values = payload.model_dump(exclude_unset=True)
    if "game_slug" in values:
        values["game_slug"] = normalize_slug(values["game_slug"])
    for field, value in values.items():
        setattr(entry, field, value)
    await db.commit()
    await db.refresh(entry)
    return to_response(entry, await ranking_position(entry, db))


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ranking_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> None:
    entry = await db.get(RankingEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Pontuação não encontrada")
    await db.delete(entry)
    await db.commit()


async def ranking_position(entry: RankingEntry, db: AsyncSession) -> int:
    position_query = (
        select(func.count())
        .select_from(RankingEntry)
        .where(
            RankingEntry.game_slug == entry.game_slug,
            (RankingEntry.score > entry.score)
            | (
                (RankingEntry.score == entry.score)
                & (RankingEntry.duration_ms < entry.duration_ms)
            ),
        )
    )
    return (await db.scalar(position_query) or 0) + 1
