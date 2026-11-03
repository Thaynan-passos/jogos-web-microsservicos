from typing import Annotated
from uuid import UUID

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.services.user_service import get_user_by_id
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: DatabaseSession
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = UUID(str(payload.get("sub")))
    except (ValueError, TypeError):
        raise credentials_exception from None

    user = await get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_admin_user(current_user: CurrentUser) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a gerentes",
        )
    return current_user


AdminUser = Annotated[User, Depends(get_admin_user)]
