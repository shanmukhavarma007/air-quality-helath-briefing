from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("At least 8 characters required")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Must contain an uppercase letter")
        if not re.search(r'[0-9]', v):
            raise ValueError("Must contain a number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Must contain a special character")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not 2 <= len(v) <= 100:
            raise ValueError("Name must be 2–100 characters")
        if not re.match(r"^[a-zA-Z\s\-']+$", v):
            raise ValueError("Name contains invalid characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str
