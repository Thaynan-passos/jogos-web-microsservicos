from datetime import datetime
from uuid import UUID

from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AdminUserCreate(UserCreate):
    is_admin: bool = False


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None
    is_active: bool | None = None
    is_admin: bool | None = None

    @field_validator("username", "email", "is_active", "is_admin")
    @classmethod
    def update_values_cannot_be_null(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Este campo não pode ser nulo")
        return value


class UserLogin(BaseModel):
    username: str = Field(min_length=1, description="Username or email")
    password: str = Field(min_length=1)


class UserResetPasswordInternal(BaseModel):
    email: EmailStr
    new_password: str = Field(min_length=8, max_length=128)
    recovery_token_id: str = Field(min_length=36, max_length=36)


class UserBatchRequest(BaseModel):
    user_ids: list[UUID] = Field(default_factory=list, max_length=100)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
