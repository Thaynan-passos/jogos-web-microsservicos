from typing import Annotated

from app.api.auth import AdminPrincipal, OptionalPrincipal
from app.db.session import get_db
from app.models.game import Game
from app.schemas.game import GameCreate, GameResponse, GameUpdate
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/games", tags=["games"])
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    payload: GameCreate, _: AdminPrincipal, db: DatabaseSession
) -> Game:
    game = Game(**payload.model_dump())
    db.add(game)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um jogo com esse identificador",
        ) from None
    await db.refresh(game)
    return game


@router.get("", response_model=list[GameResponse])
async def list_games(
    principal: OptionalPrincipal,
    include_disabled: bool = Query(False),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> list[Game]:
    if include_disabled and (principal is None or not principal.is_admin):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
                if principal is None
                else status.HTTP_403_FORBIDDEN
            ),
            detail="Acesso restrito a gerentes",
        )
    query = select(Game).order_by(Game.name)
    if not include_disabled:
        query = query.where(Game.enabled.is_(True))
    result = await db.scalars(query)
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


@router.put("/{game_slug}", response_model=GameResponse)
async def update_game(
    game_slug: str,
    payload: GameUpdate,
    _: AdminPrincipal,
    db: DatabaseSession,
) -> Game:
    game = await db.get(Game, game_slug)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Jogo não encontrado"
        )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(game, field, value)
    await db.commit()
    await db.refresh(game)
    return game


@router.delete("/{game_slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(
    game_slug: str, _: AdminPrincipal, db: DatabaseSession
) -> None:
    game = await db.get(Game, game_slug)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Jogo não encontrado"
        )
    game.enabled = False
    await db.commit()
