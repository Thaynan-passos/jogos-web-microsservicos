from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

import httpx
from app.core.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


@dataclass(frozen=True)
class Principal:
    id: UUID
    username: str
    is_admin: bool


async def get_current_principal(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> Principal:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"require_exp": True, "require_sub": True},
        )
        user_id = UUID(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas ou expiradas",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.USER_SERVICE_URL.rstrip('/')}/api/v1/users/me",
                headers={"Authorization": f"Bearer {token}"},
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível validar o usuário",
        ) from None

    if response.status_code != status.HTTP_200_OK:
        if response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de autenticação indisponível",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas ou expiradas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = response.json()
        current_id = UUID(user["id"])
        username = user["username"]
        is_admin = user["is_admin"]
        if current_id != user_id or not isinstance(username, str) or not isinstance(is_admin, bool):
            raise ValueError("Invalid user response")
        return Principal(id=current_id, username=username, is_admin=is_admin)
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas ou expiradas",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


CurrentPrincipal = Annotated[Principal, Depends(get_current_principal)]


async def get_admin_principal(principal: CurrentPrincipal) -> Principal:
    if not principal.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a gerentes",
        )
    return principal


AdminPrincipal = Annotated[Principal, Depends(get_admin_principal)]
