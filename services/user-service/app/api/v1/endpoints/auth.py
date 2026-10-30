from typing import Annotated

from app.api.dependencies import DatabaseSession
from app.core.security import create_access_token
from app.schemas.user import (
    Token,
    UserCreate,
    UserLogin,
    UserResetPasswordInternal,
    UserResponse,
)
from app.services.user_service import (
    authenticate_user,
    create_user,
    get_user_by_login,
    update_user_password,
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_in: UserCreate, db: DatabaseSession) -> UserResponse:
    if await get_user_by_login(db, user_in.username) or await get_user_by_login(
        db, str(user_in.email)
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    try:
        user = await create_user(db, user_in)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="User login with JSON payload",
    description="Accepts username (or email) and password as JSON.",
)
async def login_json(
    login_in: UserLogin,
    db: DatabaseSession,
) -> Token:
    user = await authenticate_user(db, login_in.username, login_in.password)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        user.id,
        extra_claims={"username": user.username, "is_admin": user.is_admin},
    )
    return Token(access_token=access_token)


@router.post(
    "/token",
    response_model=Token,
    summary="OAuth2 compatible token login (form-data)",
    description="Accepts username and password as form url-encoded data for OAuth2/Swagger.",
)
async def login_form(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DatabaseSession,
) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        user.id,
        extra_claims={"username": user.username, "is_admin": user.is_admin},
    )
    return Token(access_token=access_token)


@router.post(
    "/reset-password-internal",
    summary="Internal endpoint to reset user password",
    status_code=status.HTTP_200_OK,
)
async def reset_password_internal(
    payload: UserResetPasswordInternal,
    db: DatabaseSession,
) -> dict[str, str]:
    user = await update_user_password(db, str(payload.email), payload.new_password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {"message": "Password successfully updated"}
