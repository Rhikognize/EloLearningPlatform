from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$"
    )
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if not any(c.isdigit() for c in value):
            raise ValueError("Parola trebuie să conțină cel puțin o cifră")
        if not any(c.isalpha() for c in value):
            raise ValueError("Parola trebuie să conțină cel puțin o literă")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
