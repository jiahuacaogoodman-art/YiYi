from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user, require_admin
from app.core.exceptions import AppError
from app.db.base import utc_now
from app.models.feedback import QuestionFeedback
from app.models.question import Question
from app.models.user import User
from app.schemas.common import MessageOut, PageOut
from app.schemas.feedback import FeedbackCreate, FeedbackOut, FeedbackUpdate
from app.services.log_service import log_operation
from app.utils.pagination import paginate

router = APIRouter(tags=["反馈纠错"])


@router.post("/questions/{question_id}/feedback", response_model=FeedbackOut)
def create_feedback(
    question_id: int,
    payload: FeedbackCreate,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> QuestionFeedback:
    question = db.get(Question, question_id)
    if not question or question.deleted_at:
        raise AppError("题目不存在", 404)
    feedback = QuestionFeedback(
        question_id=question_id,
        user_id=current_user.id,
        feedback_type=payload.feedback_type,
        content=payload.content,
        status="pending",
    )
    question.feedback_count += 1
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/admin/feedback", response_model=PageOut)
def list_feedback(
    db: Session = Depends(db_session),
    _: User = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    status: str | None = None,
    feedback_type: str | None = None,
    question_id: int | None = None,
) -> PageOut:
    stmt = select(QuestionFeedback).where(QuestionFeedback.deleted_at.is_(None))
    if status:
        stmt = stmt.where(QuestionFeedback.status == status)
    if feedback_type:
        stmt = stmt.where(QuestionFeedback.feedback_type == feedback_type)
    if question_id:
        stmt = stmt.where(QuestionFeedback.question_id == question_id)
    stmt = stmt.order_by(QuestionFeedback.created_at.desc())
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(total=total, page=page, page_size=page_size, items=items)


@router.put("/admin/feedback/{feedback_id}", response_model=FeedbackOut)
def update_feedback(
    feedback_id: int,
    payload: FeedbackUpdate,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> QuestionFeedback:
    feedback = db.get(QuestionFeedback, feedback_id)
    if not feedback or feedback.deleted_at:
        raise AppError("反馈不存在", 404)
    feedback.status = payload.status
    feedback.handler_note = payload.handler_note
    feedback.handler_id = admin.id
    feedback.handled_at = utc_now()
    log_operation(db, admin, "handle_feedback", "question_feedback", f"处理纠错反馈：{feedback.id}", feedback.id)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.delete("/admin/feedback/{feedback_id}", response_model=MessageOut)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    feedback = db.get(QuestionFeedback, feedback_id)
    if feedback and not feedback.deleted_at:
        feedback.deleted_at = utc_now()
        log_operation(db, admin, "delete_feedback", "question_feedback", f"删除纠错反馈：{feedback.id}", feedback.id)
        db.commit()
    return MessageOut(message="反馈已删除")

