from app.db.session import get_db
from app.models.game import Game
from app.schemas.game import GameResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/games", tags=["games"])


@router.get("", response_model=list[GameResponse])
async def list_games(db: AsyncSession = Depends(get_db)) -> list[Game]:  # noqa: B008
    result = await db.scalars(
        select(Game).where(Game.enabled.is_(True)).order_by(Game.name)
    )
    return list(result.all())


@router.get("/{game_slug}", response_model=GameResponse)
async def get_game(
    game_slug: str,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> Game:
    game = await db.get(Game, game_slug)
    if game is None or not game.enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jogo não encontrado",
        )
    return game
