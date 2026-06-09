from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.practice import QuestionComment, QuestionLike, UserFavorite, UserNote
from app.models.question import Question
from app.models.taxonomy import Chapter, KnowledgePoint, Subject


def question_tags(question: Question) -> list[str]:
    return [tag.tag for tag in question.tags if tag.deleted_at is None]


def serialize_question(db: Session, question: Question, user_id: int | None = None, detail: bool = True) -> dict:
    subject_name = question.subject.name if question.subject else None
    chapter_name = question.chapter.name if question.chapter else None
    kp_name = question.knowledge_point.name if question.knowledge_point else None
    is_favorited = False
    is_liked = False
    if user_id is not None:
        is_favorited = (
            db.scalar(
                select(func.count(UserFavorite.id)).where(
                    UserFavorite.user_id == user_id,
                    UserFavorite.question_id == question.id,
                    UserFavorite.deleted_at.is_(None),
                )
            )
            or 0
        ) > 0
        is_liked = (
            db.scalar(
                select(func.count(QuestionLike.id)).where(
                    QuestionLike.user_id == user_id,
                    QuestionLike.question_id == question.id,
                    QuestionLike.deleted_at.is_(None),
                )
            )
            or 0
        ) > 0
    note_count = 0
    if user_id is not None:
        note_count = (
            db.scalar(
                select(func.count(UserNote.id)).where(
                    UserNote.user_id == user_id,
                    UserNote.question_id == question.id,
                    UserNote.deleted_at.is_(None),
                )
            )
            or 0
        )
    comment_count = (
        db.scalar(
            select(func.count(QuestionComment.id)).where(
                QuestionComment.question_id == question.id,
                QuestionComment.deleted_at.is_(None),
            )
        )
        or 0
    )
    like_count = (
        db.scalar(
            select(func.count(QuestionLike.id)).where(
                QuestionLike.question_id == question.id,
                QuestionLike.deleted_at.is_(None),
            )
        )
        or 0
    )
    data = {
        "id": question.id,
        "stem": question.stem,
        "question_type": question.question_type,
        "correct_answer": question.correct_answer,
        "analysis": question.analysis,
        "subject_id": question.subject_id,
        "chapter_id": question.chapter_id,
        "knowledge_point_id": question.knowledge_point_id,
        "subject_name": subject_name,
        "chapter_name": chapter_name,
        "knowledge_point_name": kp_name,
        "difficulty": question.difficulty,
        "importance": question.importance,
        "source": question.source,
        "year": question.year,
        "school": question.school,
        "has_image": question.has_image,
        "stem_image_url": question.stem_image_url,
        "analysis_image_url": question.analysis_image_url,
        "status": question.status,
        "practice_count": question.practice_count,
        "correct_count": question.correct_count,
        "wrong_count": question.wrong_count,
        "correct_rate": question.correct_rate,
        "favorite_count": question.favorite_count,
        "feedback_count": question.feedback_count,
        "note_count": note_count,
        "comment_count": comment_count,
        "like_count": like_count,
        "tags": question_tags(question),
        "is_favorited": is_favorited,
        "is_liked": is_liked,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
    }
    if detail:
        data["options"] = [
            {
                "id": option.id,
                "option_key": option.option_key,
                "content": option.content,
                "image_url": option.image_url,
                "sort_order": option.sort_order,
            }
            for option in question.options
            if option.deleted_at is None
        ]
    return data


def count_questions_for_subject(db: Session, subject_id: int) -> int:
    return db.scalar(
        select(func.count(Question.id)).where(
            Question.subject_id == subject_id,
            Question.deleted_at.is_(None),
        )
    ) or 0


def count_questions_for_chapter(db: Session, chapter_id: int) -> int:
    return db.scalar(
        select(func.count(Question.id)).where(
            Question.chapter_id == chapter_id,
            Question.deleted_at.is_(None),
        )
    ) or 0


def count_questions_for_knowledge_point(db: Session, knowledge_point_id: int) -> int:
    return db.scalar(
        select(func.count(Question.id)).where(
            Question.knowledge_point_id == knowledge_point_id,
            Question.deleted_at.is_(None),
        )
    ) or 0


def serialize_subject(db: Session, subject: Subject, practiced_count: int = 0, correct_rate: float = 0) -> dict:
    return {
        "id": subject.id,
        "name": subject.name,
        "code": subject.code,
        "icon": subject.icon,
        "sort_order": subject.sort_order,
        "is_enabled": subject.is_enabled,
        "description": subject.description,
        "question_count": count_questions_for_subject(db, subject.id),
        "practiced_count": practiced_count,
        "correct_rate": correct_rate,
        "created_at": subject.created_at,
        "updated_at": subject.updated_at,
    }


def serialize_chapter(db: Session, chapter: Chapter) -> dict:
    return {
        "id": chapter.id,
        "subject_id": chapter.subject_id,
        "subject_name": chapter.subject.name if chapter.subject else None,
        "name": chapter.name,
        "code": chapter.code,
        "sort_order": chapter.sort_order,
        "is_enabled": chapter.is_enabled,
        "description": chapter.description,
        "question_count": count_questions_for_chapter(db, chapter.id),
        "created_at": chapter.created_at,
        "updated_at": chapter.updated_at,
    }


def serialize_knowledge_point(db: Session, kp: KnowledgePoint) -> dict:
    return {
        "id": kp.id,
        "subject_id": kp.subject_id,
        "subject_name": kp.subject.name if kp.subject else None,
        "chapter_id": kp.chapter_id,
        "chapter_name": kp.chapter.name if kp.chapter else None,
        "name": kp.name,
        "label": kp.label,
        "importance_level": kp.importance_level,
        "description": kp.description,
        "sort_order": kp.sort_order,
        "is_enabled": kp.is_enabled,
        "question_count": count_questions_for_knowledge_point(db, kp.id),
        "created_at": kp.created_at,
        "updated_at": kp.updated_at,
    }