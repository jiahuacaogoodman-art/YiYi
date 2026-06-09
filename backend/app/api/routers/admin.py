from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import db_session, require_admin, require_super_admin
from app.core.security import get_password_hash
from app.models.log import OperationLog
from app.models.practice import UserAnswer, UserFavorite, UserWrongQuestion
from app.models.settings import SystemSetting
from app.models.user import Role, User
from app.schemas.auth import AdminUserCreate, ResetPasswordIn, UserOut, UserStatusIn
from app.schemas.common import MessageOut, PageOut
from app.schemas.settings import SystemSettingOut, SystemSettingUpdate
from app.services.log_service import log_operation
from app.utils.pagination import paginate

router = APIRouter(tags=["后台运营"])


@router.post("/admin/users", response_model=UserOut)
def create_admin_user(
    payload: AdminUserCreate,
    db: Session = Depends(db_session),
    admin: User = Depends(require_super_admin),
) -> User:
    exists = db.scalar(select(User).where(User.username == payload.username))
    if exists:
        from app.core.exceptions import AppError

        raise AppError("用户名已存在", 409)
    role = db.scalar(select(Role).where(Role.name == payload.role))
    if not role:
        role = Role(name=payload.role, label="管理员", description="后台管理员")
        db.add(role)
        db.flush()
    user = User(
        username=payload.username,
        nickname=payload.nickname or payload.username,
        email=payload.email,
        phone=payload.phone,
        hashed_password=get_password_hash(payload.password),
        role_id=role.id,
        is_active=True,
    )
    db.add(user)
    db.flush()
    log_operation(db, admin, "create_admin_user", "user", f"创建管理员账号：{user.username}", user.id)
    db.commit()
    db.refresh(user)
    return user


@router.get("/admin/users", response_model=PageOut)
def list_users(
    db: Session = Depends(db_session),
    _: User = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    keyword: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
) -> PageOut:
    stmt = select(User).options(selectinload(User.role)).where(User.deleted_at.is_(None))
    if keyword:
        stmt = stmt.where((User.username.contains(keyword)) | (User.nickname.contains(keyword)))
    if role:
        stmt = stmt.join(Role).where(Role.name == role)
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    stmt = stmt.order_by(User.created_at.desc())
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[serialize_user_row(db, user) for user in items],
    )


@router.put("/admin/users/{user_id}/status", response_model=MessageOut)
def update_user_status(
    user_id: int,
    payload: UserStatusIn,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    user = db.get(User, user_id)
    if user:
        user.is_active = payload.is_active
        log_operation(db, admin, "update_user_status", "user", f"修改用户状态：{user.username}", user.id)
        db.commit()
    return MessageOut(message="用户状态已更新")


@router.post("/admin/users/{user_id}/reset-password", response_model=MessageOut)
def reset_user_password(
    user_id: int,
    payload: ResetPasswordIn,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    user = db.get(User, user_id)
    if user:
        user.hashed_password = get_password_hash(payload.new_password)
        log_operation(db, admin, "reset_user_password", "user", f"重置用户密码：{user.username}", user.id)
        db.commit()
    return MessageOut(message="密码已重置")


@router.get("/admin/logs", response_model=PageOut)
def list_operation_logs(
    db: Session = Depends(db_session),
    _: User = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    action: str | None = None,
    target_type: str | None = None,
) -> PageOut:
    stmt = select(OperationLog).where(OperationLog.deleted_at.is_(None))
    if action:
        stmt = stmt.where(OperationLog.action == action)
    if target_type:
        stmt = stmt.where(OperationLog.target_type == target_type)
    stmt = stmt.order_by(OperationLog.created_at.desc())
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[serialize_operation_log(log) for log in items],
    )


@router.get("/admin/settings", response_model=list[SystemSettingOut])
def list_settings(
    db: Session = Depends(db_session),
    _: User = Depends(require_admin),
) -> list[SystemSetting]:
    return db.scalars(select(SystemSetting).where(SystemSetting.deleted_at.is_(None)).order_by(SystemSetting.key)).all()


@router.put("/admin/settings/{key}", response_model=SystemSettingOut)
def update_setting(
    key: str,
    payload: SystemSettingUpdate,
    db: Session = Depends(db_session),
    admin: User = Depends(require_super_admin),
) -> SystemSetting:
    setting = db.scalar(select(SystemSetting).where(SystemSetting.key == key, SystemSetting.deleted_at.is_(None)))
    if setting:
        setting.value = payload.value
        if payload.description is not None:
            setting.description = payload.description
        if payload.is_public is not None:
            setting.is_public = payload.is_public
    else:
        setting = SystemSetting(
            key=key,
            value=payload.value,
            description=payload.description,
            is_public=bool(payload.is_public),
        )
        db.add(setting)
        db.flush()
    log_operation(db, admin, "update_setting", "system_setting", f"修改系统设置：{key}", setting.id)
    db.commit()
    db.refresh(setting)
    return setting


def serialize_user_row(db: Session, user: User) -> dict:
    total = db.scalar(select(func.count(UserAnswer.id)).where(UserAnswer.user_id == user.id)) or 0
    correct = db.scalar(
        select(func.count(UserAnswer.id)).where(UserAnswer.user_id == user.id, UserAnswer.is_correct.is_(True))
    ) or 0
    wrong_count = db.scalar(
        select(func.count(UserWrongQuestion.id)).where(
            UserWrongQuestion.user_id == user.id,
            UserWrongQuestion.deleted_at.is_(None),
            UserWrongQuestion.removed_at.is_(None),
        )
    ) or 0
    favorite_count = db.scalar(
        select(func.count(UserFavorite.id)).where(UserFavorite.user_id == user.id, UserFavorite.deleted_at.is_(None))
    ) or 0
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "email": user.email,
        "phone": user.phone,
        "role": {
            "id": user.role.id,
            "name": user.role.name,
            "label": user.role.label,
        },
        "is_active": user.is_active,
        "last_login_at": user.last_login_at,
        "created_at": user.created_at,
        "total_answers": total,
        "correct_rate": round(correct / total * 100, 2) if total else 0,
        "wrong_count": wrong_count,
        "favorite_count": favorite_count,
    }


def serialize_operation_log(log: OperationLog) -> dict:
    return {
        "id": log.id,
        "operator_id": log.operator_id,
        "operator_name": log.operator.username if log.operator else None,
        "action": log.action,
        "target_type": log.target_type,
        "target_id": log.target_id,
        "summary": log.summary,
        "ip_address": log.ip_address,
        "created_at": log.created_at,
        "updated_at": log.updated_at,
    }