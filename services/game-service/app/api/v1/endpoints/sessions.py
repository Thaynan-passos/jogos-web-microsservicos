import uuid
from datetime import UTC, datetime

from app.db.session import get_db
from app.models.game import Game, GameSession
from app.schemas.session import SessionCreate, SessionResponse, SessionResult
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/sessions", tags=["sessions"])


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
