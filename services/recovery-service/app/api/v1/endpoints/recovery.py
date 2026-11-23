import asyncio
import logging
import smtplib
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from uuid import uuid4

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
        "jti": str(uuid4()),
    }
    return jwt.encode(
        to_encode, settings.RECOVERY_TOKEN_SECRET_KEY, algorithm=settings.ALGORITHM
    )


def decode_recovery_token(token: str) -> tuple[str, str]:
    try:
        payload = jwt.decode(
            token,
            settings.RECOVERY_TOKEN_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "password_recovery":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido para recuperação de senha",
            )
        email: str | None = payload.get("sub")
        token_id: str | None = payload.get("jti")
        if not email or not token_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token não contém identificação de usuário",
            )
        return email, token_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado ou inválido",
        )


def deliver_recovery_email(recipient: str, token: str) -> None:
    if not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL:
        raise RuntimeError("SMTP recovery email is not configured")

    message = EmailMessage()
    message["Subject"] = "Redefinição de senha"
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = recipient
    message.set_content(
        "Use o token abaixo para redefinir sua senha. Ele expira em "
        f"{settings.RECOVERY_TOKEN_EXPIRE_MINUTES} minutos e só pode ser usado uma vez.\n\n"
        f"{token}"
    )

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as client:
        client.starttls()
        if settings.SMTP_USERNAME:
            client.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD or "")
        client.send_message(message)


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

    logger.info("Solicitação de recuperação de senha recebida")
    if settings.ENVIRONMENT != "development":
        try:
            await asyncio.to_thread(deliver_recovery_email, email_str, token)
        except (OSError, smtplib.SMTPException, RuntimeError):
            logger.exception("Falha ao enviar e-mail de recuperação")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de recuperação temporariamente indisponível",
            ) from None

    return RecoveryRequestResponse(
        message=(
            "Solicitação de recuperação processada."
            if settings.ENVIRONMENT != "development"
            else "Utilize o token retornado para redefinir sua senha."
        ),
        email=payload.email,
        reset_token=token if settings.ENVIRONMENT == "development" else None,
        expires_in_minutes=settings.RECOVERY_TOKEN_EXPIRE_MINUTES,
    )


@router.post(
    "/verify",
    response_model=VerifyTokenResponse,
    summary="Verifica a validade do token de recuperação",
)
async def verify_recovery_token(payload: VerifyTokenRequest) -> VerifyTokenResponse:
    try:
        email, _ = decode_recovery_token(payload.token)
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
    email, token_id = decode_recovery_token(payload.token)

    # Comunica com o User Service para aplicar a nova senha
    target_url = (
        f"{settings.USER_SERVICE_URL.rstrip('/')}/api/v1/auth/reset-password-internal"
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                target_url,
                json={
                    "email": email,
                    "new_password": payload.new_password,
                    "recovery_token_id": token_id,
                },
                headers={"X-Internal-Secret": settings.USER_SERVICE_SHARED_SECRET},
            )

        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário associado ao token não foi encontrado no sistema",
            )
        elif response.status_code == 409:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token expirado, inválido ou já utilizado",
            )
        elif not 200 <= response.status_code < 300:
            logger.error(
                "User Service rejeitou a redefinição (status=%s)",
                response.status_code,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Falha ao atualizar a senha no serviço de usuários",
            )

        return ResetPasswordResponse(
            success=True,
            message="Sua senha foi redefinida com sucesso! Você já pode entrar com a nova senha.",
        )

    except httpx.RequestError as exc:
        logger.error(
            "Falha de conexão com User Service durante redefinição (%s)",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível conectar ao User Service para concluir a redefinição de senha",
        )
