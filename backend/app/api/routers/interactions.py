from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import db_session, get_current_user
from app.core.exceptions import AppError
from app.db.base import utc_now
from app.models.practice import QuestionComment, QuestionLike, UserNote
from app.models.question import Question
from app.models.user import User
from app.schemas.common import MessageOut, PageOut
from app.schemas.interaction import CommentIn, CommentOut, LikeStatusOut, NoteIn, NoteOut
from app.services.serializers import serialize_question
from app.utils.pagination import paginate

router = APIRouter(tags=["学习互动"])


def question_options():
    return (
        select(Question)
        .options(
            selectinload(Question.subject),
            selectinload(Question.chapter),
            selectinload(Question.knowledge_point),
            selectinload(Question.options),
            selectinload(Question.tags),
        )
    )


def require_published_question(db: Session, question_id: int) -> Question:
    question = db.scalar(
        question_options().where(
            Question.id == question_id,
            Question.deleted_at.is_(None),
            Question.status == "published",
        )
    )
    if not question:
        raise AppError("题目不存在或未发布", 404)
    return question


def serialize_note(db: Session, note: UserNote, user_id: int, include_question: bool = False) -> dict:
    data = {
        "id": note.id,
        "question_id": note.question_id,
        "content": note.content,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
        "question": None,
    }
    if include_question and note.question:
        data["question"] = serialize_question(db, note.question, user_id)
    return data


def serialize_comment(db: Session, comment: QuestionComment, user_id: int, include_question: bool = False) -> dict:
    data = {
        "id": comment.id,
        "question_id": comment.question_id,
        "content": comment.content,
        "is_pinned": comment.is_pinned,
        "user_id": comment.user_id,
        "username": comment.user.username if comment.user else "",
        "nickname": comment.user.nickname if comment.user else "",
        "created_at": comment.created_at,
        "updated_at": comment.updated_at,
        "is_mine": comment.user_id == user_id,
        "question": None,
    }
    if include_question and comment.question:
        data["question"] = serialize_question(db, comment.question, user_id)
    return data


def like_status(db: Session, question_id: int, user_id: int) -> LikeStatusOut:
    active_like = db.scalar(
        select(QuestionLike).where(
            QuestionLike.user_id == user_id,
            QuestionLike.question_id == question_id,
            QuestionLike.deleted_at.is_(None),
        )
    )
    count = (
        db.scalar(
            select(func.count(QuestionLike.id)).where(
                QuestionLike.question_id == question_id,
                QuestionLike.deleted_at.is_(None),
            )
        )
        or 0
    )
    return LikeStatusOut(question_id=question_id, is_liked=bool(active_like), like_count=count)


@router.get("/questions/{question_id}/notes", response_model=PageOut)
def list_question_notes(
    question_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
) -> PageOut:
    require_published_question(db, question_id)
    stmt = (
        select(UserNote)
        .where(
            UserNote.user_id == current_user.id,
            UserNote.question_id == question_id,
            UserNote.deleted_at.is_(None),
        )
        .order_by(UserNote.updated_at.desc(), UserNote.id.desc())
    )
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[serialize_note(db, item, current_user.id) for item in items],
    )


@router.post("/questions/{question_id}/notes", response_model=NoteOut)
def create_question_note(
    question_id: int,
    payload: NoteIn,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    require_published_question(db, question_id)
    note = UserNote(user_id=current_user.id, question_id=question_id, content=payload.content.strip())
    db.add(note)
    db.commit()
    db.refresh(note)
    return serialize_note(db, note, current_user.id)


@router.put("/notes/{note_id}", response_model=NoteOut)
def update_note(
    note_id: int,
    payload: NoteIn,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    note = db.scalar(
        select(UserNote).where(
            UserNote.id == note_id,
            UserNote.user_id == current_user.id,
            UserNote.deleted_at.is_(None),
        )
    )
    if not note:
        raise AppError("笔记不存在", 404)
    note.content = payload.content.strip()
    db.commit()
    db.refresh(note)
    return serialize_note(db, note, current_user.id)


@router.delete("/notes/{note_id}", response_model=MessageOut)
def delete_note(
    note_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> MessageOut:
    note = db.scalar(
        select(UserNote).where(
            UserNote.id == note_id,
            UserNote.user_id == current_user.id,
            UserNote.deleted_at.is_(None),
        )
    )
    if note:
        note.deleted_at = utc_now()
        db.commit()
    return MessageOut(message="笔记已删除")


@router.get("/me/notes", response_model=PageOut)
def my_notes(
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
) -> PageOut:
    stmt = (
        select(UserNote)
        .options(
            selectinload(UserNote.question).selectinload(Question.subject),
            selectinload(UserNote.question).selectinload(Question.chapter),
            selectinload(UserNote.question).selectinload(Question.knowledge_point),
            selectinload(UserNote.question).selectinload(Question.options),
            selectinload(UserNote.question).selectinload(Question.tags),
        )
        .join(Question, UserNote.question_id == Question.id)
        .where(
            UserNote.user_id == current_user.id,
            UserNote.deleted_at.is_(None),
            Question.deleted_at.is_(None),
        )
        .order_by(UserNote.updated_at.desc(), UserNote.id.desc())
    )
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[serialize_note(db, item, current_user.id, include_question=True) for item in items],
    )


@router.get("/questions/{question_id}/comments", response_model=PageOut)
def list_question_comments(
    question_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
) -> PageOut:
    require_published_question(db, question_id)
    stmt = (
        select(QuestionComment)
        .options(selectinload(QuestionComment.user))
        .where(
            QuestionComment.question_id == question_id,
            QuestionComment.deleted_at.is_(None),
        )
        .order_by(QuestionComment.is_pinned.desc(), QuestionComment.created_at.desc(), QuestionComment.id.desc())
    )
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[serialize_comment(db, item, current_user.id) for item in items],
    )


@router.post("/questions/{question_id}/comments", response_model=CommentOut)
def create_question_comment(
    question_id: int,
    payload: CommentIn,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    require_published_question(db, question_id)
    comment = QuestionComment(user_id=current_user.id, question_id=question_id, content=payload.content.strip())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    comment = db.scalar(select(QuestionComment).options(selectinload(QuestionComment.user)).where(QuestionComment.id == comment.id))
    return serialize_comment(db, comment, current_user.id)


@router.put("/comments/{comment_id}", response_model=CommentOut)
def update_comment(
    comment_id: int,
    payload: CommentIn,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    comment = db.scalar(
        select(QuestionComment)
        .options(selectinload(QuestionComment.user))
        .where(
            QuestionComment.id == comment_id,
            QuestionComment.user_id == current_user.id,
            QuestionComment.deleted_at.is_(None),
        )
    )
    if not comment:
        raise AppError("评论不存在", 404)
    comment.content = payload.content.strip()
    db.commit()
    db.refresh(comment)
    return serialize_comment(db, comment, current_user.id)


@router.delete("/comments/{comment_id}", response_model=MessageOut)
def delete_comment(
    comment_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> MessageOut:
    comment = db.scalar(
        select(QuestionComment).where(
            QuestionComment.id == comment_id,
            QuestionComment.user_id == current_user.id,
            QuestionComment.deleted_at.is_(None),
        )
    )
    if comment:
        comment.deleted_at = utc_now()
        db.commit()
    return MessageOut(message="评论已删除")


@router.get("/me/comments", response_model=PageOut)
def my_comments(
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
) -> PageOut:
    stmt = (
        select(QuestionComment)
        .options(
            selectinload(QuestionComment.user),
            selectinload(QuestionComment.question).selectinload(Question.subject),
            selectinload(QuestionComment.question).selectinload(Question.chapter),
            selectinload(QuestionComment.question).selectinload(Question.knowledge_point),
            selectinload(QuestionComment.question).selectinload(Question.options),
            selectinload(QuestionComment.question).selectinload(Question.tags),
        )
        .join(Question, QuestionComment.question_id == Question.id)
        .where(
            QuestionComment.user_id == current_user.id,
            QuestionComment.deleted_at.is_(None),
            Question.deleted_at.is_(None),
        )
        .order_by(QuestionComment.updated_at.desc(), QuestionComment.id.desc())
    )
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[serialize_comment(db, item, current_user.id, include_question=True) for item in items],
    )


@router.get("/questions/{question_id}/like", response_model=LikeStatusOut)
def get_question_like(
    question_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> LikeStatusOut:
    require_published_question(db, question_id)
    return like_status(db, question_id, current_user.id)


@router.post("/questions/{question_id}/like", response_model=LikeStatusOut)
def like_question(
    question_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> LikeStatusOut:
    require_published_question(db, question_id)
    record = db.scalar(
        select(QuestionLike).where(
            QuestionLike.user_id == current_user.id,
            QuestionLike.question_id == question_id,
        )
    )
    if record:
        record.deleted_at = None
    else:
        db.add(QuestionLike(user_id=current_user.id, question_id=question_id))
    db.commit()
    return like_status(db, question_id, current_user.id)


@router.delete("/questions/{question_id}/like", response_model=LikeStatusOut)
def unlike_question(
    question_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> LikeStatusOut:
    require_published_question(db, question_id)
    record = db.scalar(
        select(QuestionLike).where(
            QuestionLike.user_id == current_user.id,
            QuestionLike.question_id == question_id,
            QuestionLike.deleted_at.is_(None),
        )
    )
    if record:
        record.deleted_at = utc_now()
        db.commit()
    return like_status(db, question_id, current_user.id)


@router.get("/me/likes", response_model=PageOut)
def my_likes(
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
) -> PageOut:
    stmt = (
        select(QuestionLike)
        .options(
            selectinload(QuestionLike.question).selectinload(Question.subject),
            selectinload(QuestionLike.question).selectinload(Question.chapter),
            selectinload(QuestionLike.question).selectinload(Question.knowledge_point),
            selectinload(QuestionLike.question).selectinload(Question.options),
            selectinload(QuestionLike.question).selectinload(Question.tags),
        )
        .join(Question, QuestionLike.question_id == Question.id)
        .where(
            QuestionLike.user_id == current_user.id,
            QuestionLike.deleted_at.is_(None),
            Question.deleted_at.is_(None),
        )
        .order_by(QuestionLike.created_at.desc(), QuestionLike.id.desc())
    )
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[serialize_question(db, item.question, current_user.id) for item in items],
    )