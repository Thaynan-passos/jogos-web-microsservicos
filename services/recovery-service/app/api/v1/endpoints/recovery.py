import logging
from datetime import UTC, datetime, timedelta

import httpx
from app.core.config import settings
from app.schemas.recovery import (
    RecoveryRequest,
    RecoveryRequestResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    VerifyTokenRequest,
    VerifyTokenResponse,
)
from fastapi import APIRouter, HTTPException, status
from jose import JWTError, jwt

logger = logging.getLogger("recovery_service")
router = APIRouter(prefix="/recovery", tags=["recovery"])


def create_recovery_token(email: str) -> str:
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.RECOVERY_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": email,
        "type": "password_recovery",
        "exp": expire,
        "iat": now,
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_recovery_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "password_recovery":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido para recuperação de senha",
            )
        email: str | None = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token não contém identificação de usuário",
            )
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado ou inválido",
        )


@router.post(
    "/request",
    response_model=RecoveryRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Solicita recuperação de senha",
)
async def request_password_recovery(
    payload: RecoveryRequest,
) -> RecoveryRequestResponse:
    email_str = str(payload.email).lower().strip()
    token = create_recovery_token(email_str)

    logger.info(f"[PASSWORD RECOVERY] Código gerado para {email_str}: {token[:12]}...")

    return RecoveryRequestResponse(
        message="Solicitação de recuperação gerada com sucesso. Em ambiente de desenvolvimento, utilize o token retornado para redefinir sua senha.",
        email=payload.email,
        reset_token=token,
        expires_in_minutes=settings.RECOVERY_TOKEN_EXPIRE_MINUTES,
    )


@router.post(
    "/verify",
    response_model=VerifyTokenResponse,
    summary="Verifica a validade do token de recuperação",
)
async def verify_recovery_token(payload: VerifyTokenRequest) -> VerifyTokenResponse:
    try:
        email = decode_recovery_token(payload.token)
        return VerifyTokenResponse(
            valid=True,
            email=email,  # type: ignore[arg-type]
            message="Token válido e pronto para uso",
        )
    except HTTPException as exc:
        return VerifyTokenResponse(
            valid=False,
            email=None,
            message=exc.detail,
        )


@router.post(
    "/reset",
    response_model=ResetPasswordResponse,
    summary="Redefine a senha utilizando o token de recuperação",
)
async def reset_password(payload: ResetPasswordRequest) -> ResetPasswordResponse:
    email = decode_recovery_token(payload.token)

    # Comunica com o User Service para aplicar a nova senha
    target_url = (
        f"{settings.USER_SERVICE_URL.rstrip('/')}/api/v1/auth/reset-password-internal"
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                target_url,
                json={"email": email, "new_password": payload.new_password},
            )

        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário associado ao token não foi encontrado no sistema",
            )
        elif response.status_code >= 400:
            logger.error(f"Erro ao contatar user-service: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Falha ao atualizar a senha no serviço de usuários",
            )

        return ResetPasswordResponse(
            success=True,
            message="Sua senha foi redefinida com sucesso! Você já pode entrar com a nova senha.",
        )

    except httpx.RequestError as exc:
        logger.error(f"Falha de conexão com user-service ({target_url}): {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível conectar ao User Service para concluir a redefinição de senha",
        )
