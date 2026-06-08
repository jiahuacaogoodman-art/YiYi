from __future__ import annotations

import random

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import db_session, get_current_user
from app.core.exceptions import AppError
from app.db.base import utc_now
from app.models.practice import UserAnswer, UserFavorite, UserWrongQuestion
from app.models.question import Question
from app.models.user import User
from app.schemas.common import MessageOut, PageOut
from app.schemas.practice import PracticeAnswerIn, PracticeAnswerOut, PracticeStartIn, PracticeStartOut
from app.services.scoring import is_answer_correct, update_question_stats
from app.services.serializers import serialize_question
from app.utils.pagination import paginate

router = APIRouter(tags=["刷题"])


def question_query():
    return (
        select(Question)
        .options(
            selectinload(Question.subject),
            selectinload(Question.chapter),
            selectinload(Question.knowledge_point),
            selectinload(Question.options),
            selectinload(Question.tags),
        )
        .where(Question.deleted_at.is_(None), Question.status == "published")
    )


@router.post("/practice/start", response_model=PracticeStartOut)
def start_practice(
    payload: PracticeStartIn,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> PracticeStartOut:
    stmt = question_query()
    if payload.subject_id:
        stmt = stmt.where(Question.subject_id == payload.subject_id)
    if payload.chapter_id:
        stmt = stmt.where(Question.chapter_id == payload.chapter_id)
    if payload.knowledge_point_id:
        stmt = stmt.where(Question.knowledge_point_id == payload.knowledge_point_id)

    if payload.mode == "wrong":
        wrong_ids = select(UserWrongQuestion.question_id).where(
            UserWrongQuestion.user_id == current_user.id,
            UserWrongQuestion.deleted_at.is_(None),
            UserWrongQuestion.removed_at.is_(None),
        )
        stmt = stmt.where(Question.id.in_(wrong_ids))
    elif payload.mode == "favorites":
        favorite_ids = select(UserFavorite.question_id).where(
            UserFavorite.user_id == current_user.id,
            UserFavorite.deleted_at.is_(None),
        )
        stmt = stmt.where(Question.id.in_(favorite_ids))
    elif payload.mode == "unanswered":
        answered_ids = select(UserAnswer.question_id).where(UserAnswer.user_id == current_user.id)
        stmt = stmt.where(~Question.id.in_(answered_ids))
    elif payload.mode == "high_wrong":
        stmt = stmt.order_by(Question.wrong_count.desc(), Question.practice_count.desc())
    elif payload.mode == "random":
        questions = db.scalars(stmt).all()
        random.shuffle(questions)
        selected = questions[: payload.question_count]
        return PracticeStartOut(
            mode=payload.mode,
            total=len(selected),
            questions=[serialize_question(db, question, current_user.id) for question in selected],
        )

    if payload.mode != "high_wrong":
        stmt = stmt.order_by(Question.id.asc())
    selected = db.scalars(stmt.limit(payload.question_count)).all()
    return PracticeStartOut(
        mode=payload.mode,
        total=len(selected),
        questions=[serialize_question(db, question, current_user.id) for question in selected],
    )


@router.post("/practice/answer", response_model=PracticeAnswerOut)
def submit_answer(
    payload: PracticeAnswerIn,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> PracticeAnswerOut:
    question = db.scalar(question_query().where(Question.id == payload.question_id))
    if not question:
        raise AppError("题目不存在或未发布", 404)
    correct = is_answer_correct(question, payload.answer)
    update_question_stats(question, correct)
    db.add(
        UserAnswer(
            user_id=current_user.id,
            question_id=question.id,
            answer=payload.answer,
            is_correct=correct,
            mode=payload.mode,
            time_spent_seconds=payload.time_spent_seconds,
        )
    )

    wrong_count = 0
    added_to_wrong_book = False
    wrong_record = db.scalar(
        select(UserWrongQuestion).where(
            UserWrongQuestion.user_id == current_user.id,
            UserWrongQuestion.question_id == question.id,
        )
    )
    if correct:
        if wrong_record:
            wrong_record.last_answer_correct = True
            wrong_record.removed_at = None
            wrong_count = wrong_record.wrong_count
    else:
        added_to_wrong_book = True
        if wrong_record:
            wrong_record.wrong_count += 1
            wrong_record.last_wrong_at = utc_now()
            wrong_record.last_answer_correct = False
            wrong_record.removed_at = None
        else:
            wrong_record = UserWrongQuestion(
                user_id=current_user.id,
                question_id=question.id,
                wrong_count=1,
                last_wrong_at=utc_now(),
                last_answer_correct=False,
            )
            db.add(wrong_record)
        wrong_count = wrong_record.wrong_count
    db.commit()
    return PracticeAnswerOut(
        question_id=question.id,
        is_correct=correct,
        correct_answer=question.correct_answer,
        analysis=question.analysis,
        added_to_wrong_book=added_to_wrong_book,
        wrong_count=wrong_count,
        question_stat={
            "practice_count": question.practice_count,
            "correct_count": question.correct_count,
            "wrong_count": question.wrong_count,
            "correct_rate": question.correct_rate,
        },
    )


@router.get("/practice/wrong", response_model=PageOut)
def wrong_questions(
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    subject_id: int | None = None,
    chapter_id: int | None = None,
    knowledge_point_id: int | None = None,
    sort: str = "recent",
) -> PageOut:
    stmt = (
        select(UserWrongQuestion)
        .options(
            selectinload(UserWrongQuestion.question).selectinload(Question.subject),
            selectinload(UserWrongQuestion.question).selectinload(Question.chapter),
            selectinload(UserWrongQuestion.question).selectinload(Question.knowledge_point),
            selectinload(UserWrongQuestion.question).selectinload(Question.options),
            selectinload(UserWrongQuestion.question).selectinload(Question.tags),
        )
        .join(Question, UserWrongQuestion.question_id == Question.id)
        .where(
            UserWrongQuestion.user_id == current_user.id,
            UserWrongQuestion.deleted_at.is_(None),
            UserWrongQuestion.removed_at.is_(None),
            Question.deleted_at.is_(None),
        )
    )
    if subject_id:
        stmt = stmt.where(Question.subject_id == subject_id)
    if chapter_id:
        stmt = stmt.where(Question.chapter_id == chapter_id)
    if knowledge_point_id:
        stmt = stmt.where(Question.knowledge_point_id == knowledge_point_id)
    if sort == "wrong_count":
        stmt = stmt.order_by(UserWrongQuestion.wrong_count.desc())
    else:
        stmt = stmt.order_by(UserWrongQuestion.last_wrong_at.desc())
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[
            {
                "id": item.id,
                "question": serialize_question(db, item.question, current_user.id),
                "wrong_count": item.wrong_count,
                "last_wrong_at": item.last_wrong_at,
                "last_answer_correct": item.last_answer_correct,
            }
            for item in items
        ],
    )


@router.delete("/practice/wrong/{question_id}", response_model=MessageOut)
def remove_wrong_question(
    question_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> MessageOut:
    wrong_record = db.scalar(
        select(UserWrongQuestion).where(
            UserWrongQuestion.user_id == current_user.id,
            UserWrongQuestion.question_id == question_id,
            UserWrongQuestion.deleted_at.is_(None),
        )
    )
    if wrong_record:
        wrong_record.removed_at = utc_now()
        db.commit()
    return MessageOut(message="已移出错题本")


@router.get("/practice/favorites", response_model=PageOut)
def favorite_questions(
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    subject_id: int | None = None,
    chapter_id: int | None = None,
    difficulty: str | None = None,
) -> PageOut:
    stmt = (
        select(UserFavorite)
        .options(
            selectinload(UserFavorite.question).selectinload(Question.subject),
            selectinload(UserFavorite.question).selectinload(Question.chapter),
            selectinload(UserFavorite.question).selectinload(Question.knowledge_point),
            selectinload(UserFavorite.question).selectinload(Question.options),
            selectinload(UserFavorite.question).selectinload(Question.tags),
        )
        .join(Question, UserFavorite.question_id == Question.id)
        .where(
            UserFavorite.user_id == current_user.id,
            UserFavorite.deleted_at.is_(None),
            Question.deleted_at.is_(None),
        )
    )
    if subject_id:
        stmt = stmt.where(Question.subject_id == subject_id)
    if chapter_id:
        stmt = stmt.where(Question.chapter_id == chapter_id)
    if difficulty:
        stmt = stmt.where(Question.difficulty == difficulty)
    stmt = stmt.order_by(UserFavorite.created_at.desc())
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[serialize_question(db, item.question, current_user.id) for item in items],
    )


@router.post("/questions/{question_id}/favorite", response_model=MessageOut)
def favorite_question(
    question_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> MessageOut:
    question = db.get(Question, question_id)
    if not question or question.deleted_at or question.status != "published":
        raise AppError("题目不存在或未发布", 404)
    favorite = db.scalar(
        select(UserFavorite).where(
            UserFavorite.user_id == current_user.id,
            UserFavorite.question_id == question_id,
        )
    )
    if favorite:
        if favorite.deleted_at is not None:
            favorite.deleted_at = None
            question.favorite_count += 1
    else:
        db.add(UserFavorite(user_id=current_user.id, question_id=question_id))
        question.favorite_count += 1
    db.commit()
    return MessageOut(message="已收藏")


@router.delete("/questions/{question_id}/favorite", response_model=MessageOut)
def unfavorite_question(
    question_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> MessageOut:
    favorite = db.scalar(
        select(UserFavorite).where(
            UserFavorite.user_id == current_user.id,
            UserFavorite.question_id == question_id,
            UserFavorite.deleted_at.is_(None),
        )
    )
    if favorite:
        favorite.deleted_at = utc_now()
        question = db.get(Question, question_id)
        if question and question.favorite_count > 0:
            question.favorite_count -= 1
        db.commit()
    return MessageOut(message="已取消收藏")
