from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.question import Question, QuestionOption, QuestionTag
from app.models.taxonomy import Chapter, KnowledgePoint, Subject
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionUpdate
from app.utils.text import normalize_answer, normalize_multi_answer, similarity

CHOICE_KEYS = {"A", "B", "C", "D", "E", "F"}
VALID_TYPES = {"single_choice", "multiple_choice", "true_false", "fill_blank", "short_answer"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_IMPORTANCE = {"normal", "key", "frequent"}
VALID_STATUS = {"draft", "pending_review", "published", "offline"}


def ensure_taxonomy(db: Session, subject_id: int, chapter_id: int, knowledge_point_id: int) -> None:
    subject = db.get(Subject, subject_id)
    chapter = db.get(Chapter, chapter_id)
    kp = db.get(KnowledgePoint, knowledge_point_id)
    if not subject or subject.deleted_at is not None:
        raise AppError("科目不存在")
    if not chapter or chapter.deleted_at is not None or chapter.subject_id != subject_id:
        raise AppError("章节不存在或不属于该科目")
    if not kp or kp.deleted_at is not None or kp.chapter_id != chapter_id:
        raise AppError("知识点不存在或不属于该章节")


def validate_question_payload(payload: QuestionCreate | QuestionUpdate, current: Question | None = None) -> None:
    q_type = payload.question_type or (current.question_type if current else None)
    if q_type not in VALID_TYPES:
        raise AppError("题型不正确")
    difficulty = payload.difficulty or (current.difficulty if current else "medium")
    if difficulty not in VALID_DIFFICULTIES:
        raise AppError("难度不正确")
    importance = payload.importance or (current.importance if current else "normal")
    if importance not in VALID_IMPORTANCE:
        raise AppError("重要程度不正确")
    status = payload.status or (current.status if current else "draft")
    if status not in VALID_STATUS:
        raise AppError("题目状态不正确")

    answer = payload.correct_answer or (current.correct_answer if current else "")
    options = payload.options
    if q_type == "single_choice":
        valid_option_keys = {
            option.option_key.strip().upper()
            for option in (options if options is not None else current.options if current else [])
        }
        if normalize_answer(answer) not in valid_option_keys:
            raise AppError("单选题答案必须是已有选项中的一个")
    if q_type == "multiple_choice":
        valid_option_keys = {
            option.option_key.strip().upper()
            for option in (options if options is not None else current.options if current else [])
        }
        answers = normalize_multi_answer(answer).split(",")
        if not answers or any(item not in valid_option_keys for item in answers):
            raise AppError("多选题答案必须在已有选项范围内")
    if q_type == "true_false" and normalize_answer(answer) not in {"A", "B", "正确", "错误", "TRUE", "FALSE"}:
        raise AppError("判断题答案必须是 A/B 或 正确/错误")


def create_question(db: Session, payload: QuestionCreate, creator: User | None = None) -> Question:
    ensure_taxonomy(db, payload.subject_id, payload.chapter_id, payload.knowledge_point_id)
    validate_question_payload(payload)
    question = Question(
        stem=payload.stem,
        question_type=payload.question_type,
        correct_answer=payload.correct_answer,
        analysis=payload.analysis,
        subject_id=payload.subject_id,
        chapter_id=payload.chapter_id,
        knowledge_point_id=payload.knowledge_point_id,
        difficulty=payload.difficulty,
        importance=payload.importance,
        source=payload.source,
        year=payload.year,
        school=payload.school,
        has_image=payload.has_image,
        stem_image_url=payload.stem_image_url,
        analysis_image_url=payload.analysis_image_url,
        status=payload.status,
        created_by_id=creator.id if creator else None,
    )
    db.add(question)
    db.flush()
    replace_options_and_tags(db, question, payload.options, payload.tags)
    return question


def update_question(db: Session, question: Question, payload: QuestionUpdate) -> Question:
    subject_id = payload.subject_id if payload.subject_id is not None else question.subject_id
    chapter_id = payload.chapter_id if payload.chapter_id is not None else question.chapter_id
    kp_id = payload.knowledge_point_id if payload.knowledge_point_id is not None else question.knowledge_point_id
    ensure_taxonomy(db, subject_id, chapter_id, kp_id)
    validate_question_payload(payload, current=question)
    for field in [
        "stem",
        "question_type",
        "correct_answer",
        "analysis",
        "subject_id",
        "chapter_id",
        "knowledge_point_id",
        "difficulty",
        "importance",
        "source",
        "year",
        "school",
        "has_image",
        "stem_image_url",
        "analysis_image_url",
        "status",
    ]:
        value = getattr(payload, field)
        if value is not None:
            setattr(question, field, value)
    if payload.options is not None or payload.tags is not None:
        replace_options_and_tags(
            db,
            question,
            payload.options if payload.options is not None else list(question.options),
            payload.tags if payload.tags is not None else [tag.tag for tag in question.tags],
        )
    return question


def replace_options_and_tags(
    db: Session,
    question: Question,
    options: list,
    tags: list[str],
) -> None:
    for option in list(question.options):
        db.delete(option)
    for tag in list(question.tags):
        db.delete(tag)
    db.flush()
    for option in options:
        db.add(
            QuestionOption(
                question_id=question.id,
                option_key=option.option_key.strip().upper(),
                content=option.content,
                image_url=option.image_url,
                sort_order=option.sort_order,
            )
        )
    for tag in tags:
        cleaned = tag.strip()
        if cleaned:
            db.add(QuestionTag(question_id=question.id, tag=cleaned))


def duplicate_candidates(db: Session, stem: str, threshold: float = 0.82, limit: int = 20) -> list[dict]:
    questions = db.scalars(
        select(Question).where(Question.deleted_at.is_(None)).order_by(Question.id.desc()).limit(5000)
    ).all()
    results = []
    compact_stem = "".join(stem.split())
    for question in questions:
        score = similarity(stem, question.stem)
        if compact_stem == "".join(question.stem.split()):
            score = 1.0
        if score >= threshold:
            results.append(
                {
                    "question_id": question.id,
                    "stem": question.stem,
                    "similarity": round(score, 4),
                    "duplicate_type": "完全重复" if score == 1 else "高度相似",
                }
            )
    return sorted(results, key=lambda item: item["similarity"], reverse=True)[:limit]

