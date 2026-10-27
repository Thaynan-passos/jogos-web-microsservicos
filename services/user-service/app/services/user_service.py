from collections.abc import Sequence
from uuid import UUID

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_by_login(db: AsyncSession, login: str) -> User | None:
    result = await db.execute(
        select(User).where(or_(User.username == login, User.email == login))
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: UUID | str) -> User | None:
    if isinstance(user_id, str):
        try:
            user_id = UUID(user_id)
        except ValueError:
            return None
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_users_by_ids(
    db: AsyncSession, user_ids: Sequence[UUID | str]
) -> Sequence[User]:
    valid_ids: list[UUID] = []
    for uid in user_ids:
        if isinstance(uid, str):
            try:
                valid_ids.append(UUID(uid))
            except ValueError:
                continue
        elif isinstance(uid, UUID):
            valid_ids.append(uid)

    if not valid_ids:
        return []

    result = await db.execute(select(User).where(User.id.in_(valid_ids)))
    return result.scalars().all()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    user = User(
        username=user_in.username,
        email=str(user_in.email),
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, login: str, password: str) -> User | None:
    user = await get_user_by_login(db, login)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user
