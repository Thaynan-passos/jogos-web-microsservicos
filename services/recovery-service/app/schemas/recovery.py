from pydantic import BaseModel, EmailStr, Field


class RecoveryRequest(BaseModel):
    email: EmailStr


class RecoveryRequestResponse(BaseModel):
    message: str
    email: EmailStr
    reset_token: str
    expires_in_minutes: int


class VerifyTokenRequest(BaseModel):
    token: str


class VerifyTokenResponse(BaseModel):
    valid: bool
    email: EmailStr | None = None
    message: str


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


class ResetPasswordResponse(BaseModel):
    success: bool
    message: str
