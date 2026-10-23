from uuid import UUID

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.user import UserBatchRequest, UserResponse
from app.services.user_service import get_user_by_id, get_users_by_ids
from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("/users/me", response_model=UserResponse)
async def read_current_user(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user_by_id(user_id: UUID, db: DatabaseSession) -> UserResponse:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserResponse.model_validate(user)


@router.post("/users/batch", response_model=list[UserResponse])
async def read_users_batch(
    payload: UserBatchRequest, db: DatabaseSession
) -> list[UserResponse]:
    users = await get_users_by_ids(db, payload.user_ids)
    return [UserResponse.model_validate(u) for u in users]
