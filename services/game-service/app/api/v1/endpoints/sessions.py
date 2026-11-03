import uuid
from datetime import UTC, datetime
from typing import Annotated

from app.db.session import get_db
from app.models.game import Game, GameSession
from app.schemas.session import (
    SessionCreate,
    SessionResponse,
    SessionResult,
    SessionUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/sessions", tags=["sessions"])
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[SessionResponse])
async def list_sessions(
    db: DatabaseSession,
    limit: int = 100,
) -> list[GameSession]:
    result = await db.scalars(
        select(GameSession).order_by(GameSession.started_at.desc()).limit(limit)
    )
    return list(result.all())


async def get_session_or_404(session_id: uuid.UUID, db: AsyncSession) -> GameSession:
    session = await db.get(GameSession, session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de jogo não encontrada",
        )
    return session


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    payload: SessionCreate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> GameSession:
    game = await db.scalar(
        select(Game).where(Game.slug == payload.game_slug, Game.enabled.is_(True))
    )
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jogo não encontrado ou desativado",
        )

    session = GameSession(game_slug=game.slug, user_id=payload.user_id)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> GameSession:
    return await get_session_or_404(session_id, db)


@router.post("/{session_id}/complete", response_model=SessionResponse)
async def complete_session(
    session_id: uuid.UUID,
    payload: SessionResult,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> GameSession:
    session = await get_session_or_404(session_id, db)
    if session.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Somente sessões em andamento podem ser concluídas",
        )

    session.status = "completed"
    session.result = payload.result
    session.completed_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(session)
    return session


@router.post("/{session_id}/abandon", response_model=SessionResponse)
async def abandon_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> GameSession:
    session = await get_session_or_404(session_id, db)
    if session.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Somente sessões em andamento podem ser abandonadas",
        )

    session.status = "abandoned"
    session.completed_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(session)
    return session


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: uuid.UUID,
    payload: SessionUpdate,
    db: DatabaseSession,
) -> GameSession:
    session = await get_session_or_404(session_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(session, field, value)
    await db.commit()
    await db.refresh(session)
    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: uuid.UUID, db: DatabaseSession) -> None:
    session = await get_session_or_404(session_id, db)
    await db.delete(session)
    await db.commit()
