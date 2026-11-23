from uuid import UUID

from app.api.dependencies import AdminUser, CurrentUser, DatabaseSession
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import AdminUserCreate, UserBatchRequest, UserResponse, UserUpdate
from app.services.user_service import get_user_by_id, get_user_by_login, get_users_by_ids
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_managed_user(
    payload: AdminUserCreate,
    _: AdminUser,
    db: DatabaseSession,
) -> UserResponse:
    if await get_user_by_login(db, payload.username) or await get_user_by_login(
        db, str(payload.email)
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Usuário já existe"
        )
    user = User(
        username=payload.username,
        email=str(payload.email),
        hashed_password=get_password_hash(payload.password),
        is_admin=payload.is_admin,
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Usuário já existe"
        ) from None
    await db.refresh(user)
    return UserResponse.model_validate(user)


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
async def read_user_by_id(
    user_id: UUID,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> UserResponse:
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    return UserResponse.model_validate(user)


@router.post("/users/batch", response_model=list[UserResponse])
async def read_users_batch(
    payload: UserBatchRequest, _: AdminUser, db: DatabaseSession
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    changes = payload.model_dump(exclude_unset=True)
    removing_active_admin = (
        user.is_admin
        and user.is_active
        and (changes.get("is_admin") is False or changes.get("is_active") is False)
    )
    if removing_active_admin:
        active_admins = list(
            await db.scalars(
                select(User)
                .where(User.is_admin.is_(True), User.is_active.is_(True))
                .with_for_update()
            )
        )
        if len(active_admins) <= 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="O último gerente ativo não pode ser desativado ou rebaixado",
            )
    for field, value in changes.items():
        setattr(user, field, value)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nome de usuário ou e-mail já está em uso",
        ) from None
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID, current_user: AdminUser, db: DatabaseSession
) -> None:
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O gerente atual não pode ser removido",
        )
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    await db.delete(user)
    await db.commit()
