from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=128)


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=6, max_length=128)
    nickname: str | None = Field(default=None, max_length=80)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)


class RoleOut(BaseModel):
    id: int
    name: str
    label: str

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: int
    username: str
    nickname: str
    email: str | None
    phone: str | None
    role: RoleOut
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListOut(BaseModel):
    id: int
    username: str
    nickname: str
    email: str | None
    phone: str | None
    role: RoleOut
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
    total_answers: int = 0
    correct_rate: float = 0
    wrong_count: int = 0
    favorite_count: int = 0

    model_config = {"from_attributes": True}


class UserStatusIn(BaseModel):
    is_active: bool


class ResetPasswordIn(BaseModel):
    new_password: str = Field(min_length=6, max_length=128)


class AdminUserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=6, max_length=128)
    nickname: str | None = Field(default=None, max_length=80)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    role: str = Field(default="admin", pattern="^(admin|super_admin)$")
