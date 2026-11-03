from uuid import UUID

from app.api.dependencies import AdminUser, CurrentUser, DatabaseSession
from app.models.user import User
from app.schemas.user import UserBatchRequest, UserResponse, UserUpdate
from app.services.user_service import get_user_by_id, get_users_by_ids
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

router = APIRouter()


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    _: AdminUser,
    db: DatabaseSession,
    limit: int = Query(100, ge=1, le=500),
) -> list[UserResponse]:
    result = await db.scalars(
        select(User).order_by(User.created_at.desc()).limit(limit)
    )
    return [UserResponse.model_validate(user) for user in result.all()]


@router.get("/users/me", response_model=UserResponse)
async def read_current_user(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user_by_id(user_id: UUID, db: DatabaseSession) -> UserResponse:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    return UserResponse.model_validate(user)


@router.post("/users/batch", response_model=list[UserResponse])
async def read_users_batch(
    payload: UserBatchRequest, db: DatabaseSession
) -> list[UserResponse]:
    users = await get_users_by_ids(db, payload.user_ids)
    return [UserResponse.model_validate(u) for u in users]


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    _: AdminUser,
    db: DatabaseSession,
) -> UserResponse:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID, current_user: AdminUser, db: DatabaseSession
) -> None:
    if user_id == current_user.id:
        raise HTTPException(
            status_code=409, detail="O gerente atual não pode ser removido"
        )
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    await db.delete(user)
    await db.commit()
