from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import Role, User
from app.schemas.auth import LoginIn, RegisterIn, TokenOut, UserOut
from app.schemas.common import MessageOut
from app.services.log_service import log_operation

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(db_session)) -> TokenOut:
    user = db.scalar(
        select(User).where(
            or_(User.username == payload.username, User.email == payload.username),
            User.deleted_at.is_(None),
        )
    )
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用")
    user.last_login_at = datetime.now(timezone.utc)
    if user.role.name in {"admin", "super_admin"}:
        log_operation(db, user, "admin_login", "user", f"管理员登录：{user.username}", user.id)
    db.commit()
    return TokenOut(access_token=create_access_token(str(user.id)))


@router.post("/register", response_model=UserOut)
def register(payload: RegisterIn, db: Session = Depends(db_session)) -> User:
    exists = db.scalar(
        select(User).where(
            or_(
                User.username == payload.username,
                User.email == payload.email,
                User.phone == payload.phone if payload.phone else False,
            )
        )
    )
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名、邮箱或手机号已被占用")
    role = db.scalar(select(Role).where(Role.name == "student"))
    if not role:
        role = Role(name="student", label="普通用户", description="学生端刷题用户")
        db.add(role)
        db.flush()
    user = User(
        username=payload.username,
        nickname=payload.nickname or payload.username,
        email=payload.email,
        phone=payload.phone,
        hashed_password=get_password_hash(payload.password),
        role_id=role.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/logout", response_model=MessageOut)
def logout() -> MessageOut:
    return MessageOut(message="已退出登录")