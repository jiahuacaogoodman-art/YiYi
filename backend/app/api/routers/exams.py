from __future__ import annotations

from datetime import timedelta
import random

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import db_session, get_current_user, require_admin
from app.core.exceptions import AppError
from app.db.base import utc_now
from app.models.exam import Exam, ExamQuestion, ExamRecord, ExamRecordAnswer
from app.models.practice import UserAnswer, UserWrongQuestion
from app.models.question import Question
from app.models.user import User
from app.schemas.common import MessageOut, PageOut
from app.schemas.exam import AutoGenerateExamIn, ExamCreate, ExamDetailOut, ExamOut, ExamRecordOut, ExamStartOut, ExamSubmitIn, ExamUpdate
from app.services.log_service import log_operation
from app.services.scoring import is_answer_correct, update_question_stats
from app.services.serializers import serialize_question
from app.utils.pagination import paginate

router = APIRouter(tags=["考试"])


def exam_query():
    return (
        select(Exam)
        .options(
            selectinload(Exam.subject),
            selectinload(Exam.questions).selectinload(ExamQuestion.question).selectinload(Question.subject),
            selectinload(Exam.questions).selectinload(ExamQuestion.question).selectinload(Question.chapter),
            selectinload(Exam.questions).selectinload(ExamQuestion.question).selectinload(Question.knowledge_point),
            selectinload(Exam.questions).selectinload(ExamQuestion.question).selectinload(Question.options),
            selectinload(Exam.questions).selectinload(ExamQuestion.question).selectinload(Question.tags),
        )
    )


def serialize_exam(db: Session, exam: Exam, include_questions: bool = False, user_id: int | None = None) -> dict:
    data = {
        "id": exam.id,
        "name": exam.name,
        "exam_type": exam.exam_type,
        "subject_id": exam.subject_id,
        "subject_name": exam.subject.name if exam.subject else None,
        "total_score": exam.total_score,
        "pass_score": exam.pass_score,
        "duration_minutes": exam.duration_minutes,
        "is_public": exam.is_public,
        "status": exam.status,
        "description": exam.description,
        "question_count": len([item for item in exam.questions if item.deleted_at is None]),
        "created_at": exam.created_at,
        "updated_at": exam.updated_at,
    }
    if include_questions:
        data["questions"] = [
            serialize_question(db, item.question, user_id)
            for item in exam.questions
            if item.deleted_at is None and item.question and item.question.deleted_at is None
        ]
    return data


@router.get("/exams", response_model=PageOut)
def list_public_exams(
    db: Session = Depends(db_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    subject_id: int | None = None,
) -> PageOut:
    stmt = exam_query().where(Exam.deleted_at.is_(None), Exam.is_public.is_(True), Exam.status == "published")
    if subject_id:
        stmt = stmt.where(Exam.subject_id == subject_id)
    stmt = stmt.order_by(Exam.created_at.desc())
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(total=total, page=page, page_size=page_size, items=[serialize_exam(db, item) for item in items])


@router.get("/exams/records/{record_id}", response_model=ExamRecordOut)
def get_exam_record(
    record_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    record = db.scalar(
        select(ExamRecord)
        .options(
            selectinload(ExamRecord.exam),
            selectinload(ExamRecord.answers).selectinload(ExamRecordAnswer.question).selectinload(Question.options),
            selectinload(ExamRecord.answers).selectinload(ExamRecordAnswer.question).selectinload(Question.tags),
        )
        .where(ExamRecord.id == record_id, ExamRecord.deleted_at.is_(None))
    )
    if not record:
        raise AppError("考试记录不存在", 404)
    if record.user_id != current_user.id and current_user.role.name == "student":
        raise AppError("无权查看该考试记录", 403)
    return serialize_exam_record(db, record, current_user.id)


@router.get("/exams/{exam_id}", response_model=ExamDetailOut)
def get_public_exam(
    exam_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    exam = db.scalar(
        exam_query().where(Exam.id == exam_id, Exam.deleted_at.is_(None), Exam.is_public.is_(True), Exam.status == "published")
    )
    if not exam:
        raise AppError("试卷不存在或未发布", 404)
    return serialize_exam(db, exam, include_questions=True, user_id=current_user.id)


@router.post("/exams/{exam_id}/start", response_model=ExamStartOut)
def start_exam(
    exam_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> ExamStartOut:
    exam = db.scalar(
        exam_query().where(Exam.id == exam_id, Exam.deleted_at.is_(None), Exam.is_public.is_(True), Exam.status == "published")
    )
    if not exam:
        raise AppError("试卷不存在或未发布", 404)
    now = utc_now()
    record = ExamRecord(exam_id=exam.id, user_id=current_user.id, started_at=now, status="in_progress")
    db.add(record)
    db.commit()
    db.refresh(record)
    return ExamStartOut(
        record_id=record.id,
        exam=serialize_exam(db, exam, include_questions=True, user_id=current_user.id),
        started_at=now,
        deadline_at=now + timedelta(minutes=exam.duration_minutes),
    )


@router.post("/exams/{exam_id}/submit", response_model=ExamRecordOut)
def submit_exam(
    exam_id: int,
    payload: ExamSubmitIn,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    record = db.scalar(
        select(ExamRecord)
        .options(selectinload(ExamRecord.exam).selectinload(Exam.questions).selectinload(ExamQuestion.question))
        .where(
            ExamRecord.id == payload.record_id,
            ExamRecord.exam_id == exam_id,
            ExamRecord.user_id == current_user.id,
            ExamRecord.deleted_at.is_(None),
        )
    )
    if not record:
        raise AppError("考试记录不存在", 404)
    if record.status == "submitted":
        raise AppError("该试卷已经提交")
    exam_questions = {item.question_id: item for item in record.exam.questions if item.deleted_at is None}
    answer_map = {item.question_id: item.answer for item in payload.answers}
    score = 0.0
    correct_count = 0
    wrong_count = 0
    for question_id, exam_question in exam_questions.items():
        question = exam_question.question
        answer = answer_map.get(question_id, "")
        correct = is_answer_correct(question, answer) if answer else False
        item_score = exam_question.score if correct else 0
        score += item_score
        correct_count += 1 if correct else 0
        wrong_count += 0 if correct else 1
        update_question_stats(question, correct)
        db.add(
            ExamRecordAnswer(
                record_id=record.id,
                question_id=question_id,
                answer=answer,
                is_correct=correct,
                score=item_score,
            )
        )
        db.add(
            UserAnswer(
                user_id=current_user.id,
                question_id=question_id,
                answer=answer,
                is_correct=correct,
                mode="exam",
            )
        )
        update_wrong_book_for_exam(db, current_user.id, question_id, correct)
    record.submitted_at = utc_now()
    record.score = round(score, 2)
    record.correct_count = correct_count
    record.wrong_count = wrong_count
    record.status = "submitted"
    db.commit()
    record = db.scalar(
        select(ExamRecord)
        .options(
            selectinload(ExamRecord.exam),
            selectinload(ExamRecord.answers).selectinload(ExamRecordAnswer.question).selectinload(Question.options),
            selectinload(ExamRecord.answers).selectinload(ExamRecordAnswer.question).selectinload(Question.tags),
        )
        .where(ExamRecord.id == record.id)
    )
    return serialize_exam_record(db, record, current_user.id)


@router.get("/admin/exams", response_model=PageOut)
def admin_list_exams(
    db: Session = Depends(db_session),
    _: User = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    subject_id: int | None = None,
    status: str | None = None,
) -> PageOut:
    stmt = exam_query().where(Exam.deleted_at.is_(None))
    if subject_id:
        stmt = stmt.where(Exam.subject_id == subject_id)
    if status:
        stmt = stmt.where(Exam.status == status)
    stmt = stmt.order_by(Exam.created_at.desc())
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(total=total, page=page, page_size=page_size, items=[serialize_exam(db, item) for item in items])


@router.post("/admin/exams", response_model=ExamDetailOut)
def admin_create_exam(
    payload: ExamCreate,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> dict:
    exam = Exam(**payload.model_dump(exclude={"questions"}), created_by_id=admin.id)
    db.add(exam)
    db.flush()
    replace_exam_questions(db, exam, payload.questions)
    log_operation(db, admin, "create_exam", "exam", f"创建试卷：{exam.name}", exam.id)
    db.commit()
    exam = db.scalar(exam_query().where(Exam.id == exam.id))
    return serialize_exam(db, exam, include_questions=True, user_id=admin.id)


@router.post("/admin/exams/auto-generate", response_model=ExamDetailOut)
def admin_auto_generate_exam(
    payload: AutoGenerateExamIn,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> dict:
    stmt = select(Question).where(
        Question.subject_id == payload.subject_id,
        Question.status == "published",
        Question.deleted_at.is_(None),
    )
    if payload.chapter_ids:
        stmt = stmt.where(Question.chapter_id.in_(payload.chapter_ids))
    questions = db.scalars(stmt).all()
    selected = select_questions_by_difficulty_ratio(
        questions,
        payload.question_count,
        {
            "easy": payload.easy_ratio,
            "medium": payload.medium_ratio,
            "hard": payload.hard_ratio,
        },
    )
    if not selected:
        raise AppError("没有可用于组卷的已发布题目")
    per_score = round(100 / len(selected), 2)
    exam = Exam(
        name=payload.name,
        exam_type="mock",
        subject_id=payload.subject_id,
        total_score=100,
        pass_score=60,
        duration_minutes=payload.duration_minutes,
        is_public=payload.is_public,
        status="published" if payload.is_public else "draft",
        created_by_id=admin.id,
    )
    db.add(exam)
    db.flush()
    replace_exam_questions(
        db,
        exam,
        [{"question_id": question.id, "score": per_score, "sort_order": index + 1} for index, question in enumerate(selected)],
    )
    log_operation(db, admin, "auto_generate_exam", "exam", f"自动组卷：{exam.name}", exam.id)
    db.commit()
    exam = db.scalar(exam_query().where(Exam.id == exam.id))
    return serialize_exam(db, exam, include_questions=True, user_id=admin.id)


def select_questions_by_difficulty_ratio(
    questions: list[Question],
    question_count: int,
    ratios: dict[str, float],
) -> list[Question]:
    buckets = {
        "easy": [question for question in questions if question.difficulty == "easy"],
        "medium": [question for question in questions if question.difficulty == "medium"],
        "hard": [question for question in questions if question.difficulty == "hard"],
    }
    for bucket in buckets.values():
        random.shuffle(bucket)
    ratio_sum = sum(ratios.values()) or 1
    targets = {
        difficulty: int(question_count * ratio / ratio_sum)
        for difficulty, ratio in ratios.items()
    }
    selected: list[Question] = []
    for difficulty in ["easy", "medium", "hard"]:
        selected.extend(buckets[difficulty][: targets.get(difficulty, 0)])
    remaining = [question for question in questions if question not in selected]
    random.shuffle(remaining)
    selected.extend(remaining[: max(0, question_count - len(selected))])
    random.shuffle(selected)
    return selected[:question_count]


@router.put("/admin/exams/{exam_id}", response_model=ExamDetailOut)
def admin_update_exam(
    exam_id: int,
    payload: ExamUpdate,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> dict:
    exam = db.scalar(exam_query().where(Exam.id == exam_id, Exam.deleted_at.is_(None)))
    if not exam:
        raise AppError("试卷不存在", 404)
    for key, value in payload.model_dump(exclude_unset=True, exclude={"questions"}).items():
        setattr(exam, key, value)
    if payload.questions is not None:
        replace_exam_questions(db, exam, payload.questions)
    log_operation(db, admin, "update_exam", "exam", f"编辑试卷：{exam.name}", exam.id)
    db.commit()
    exam = db.scalar(exam_query().where(Exam.id == exam.id))
    return serialize_exam(db, exam, include_questions=True, user_id=admin.id)


@router.post("/admin/exams/{exam_id}/publish", response_model=MessageOut)
def admin_publish_exam(
    exam_id: int,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    exam = db.get(Exam, exam_id)
    if not exam or exam.deleted_at:
        raise AppError("试卷不存在", 404)
    exam.status = "published"
    exam.is_public = True
    log_operation(db, admin, "publish_exam", "exam", f"发布试卷：{exam.name}", exam.id)
    db.commit()
    return MessageOut(message="试卷已发布")


@router.post("/admin/exams/{exam_id}/offline", response_model=MessageOut)
def admin_offline_exam(
    exam_id: int,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    exam = db.get(Exam, exam_id)
    if not exam or exam.deleted_at:
        raise AppError("试卷不存在", 404)
    exam.status = "offline"
    exam.is_public = False
    log_operation(db, admin, "offline_exam", "exam", f"下架试卷：{exam.name}", exam.id)
    db.commit()
    return MessageOut(message="试卷已下架")


@router.get("/admin/exams/{exam_id}/statistics")
def admin_exam_statistics(
    exam_id: int,
    db: Session = Depends(db_session),
    _: User = Depends(require_admin),
) -> dict:
    records = db.scalars(select(ExamRecord).where(ExamRecord.exam_id == exam_id, ExamRecord.status == "submitted")).all()
    scores = [record.score or 0 for record in records]
    answers = db.execute(
        select(
            ExamRecordAnswer.question_id,
            func.count(ExamRecordAnswer.id).label("total"),
            func.sum(case((ExamRecordAnswer.is_correct.is_(True), 1), else_=0)).label("correct"),
        )
        .join(ExamRecord, ExamRecordAnswer.record_id == ExamRecord.id)
        .where(ExamRecord.exam_id == exam_id)
        .group_by(ExamRecordAnswer.question_id)
    ).all()
    question_accuracy = [
        {
            "question_id": row.question_id,
            "total": row.total,
            "correct": int(row.correct or 0),
            "correct_rate": round((row.correct or 0) / row.total * 100, 2) if row.total else 0,
        }
        for row in answers
    ]
    return {
        "participants": len(records),
        "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
        "highest_score": max(scores) if scores else 0,
        "lowest_score": min(scores) if scores else 0,
        "question_accuracy": question_accuracy,
        "top_wrong_questions": sorted(question_accuracy, key=lambda item: item["correct_rate"])[:10],
    }


def replace_exam_questions(db: Session, exam: Exam, questions) -> None:
    for item in list(exam.questions):
        db.delete(item)
    db.flush()
    for index, item in enumerate(questions):
        if isinstance(item, dict):
            question_id = item["question_id"]
            score = item.get("score", 5)
            sort_order = item.get("sort_order", index + 1)
        else:
            question_id = item.question_id
            score = item.score
            sort_order = item.sort_order or index + 1
        question = db.get(Question, question_id)
        if not question or question.deleted_at:
            raise AppError(f"题目不存在：{question_id}")
        db.add(ExamQuestion(exam_id=exam.id, question_id=question_id, score=score, sort_order=sort_order))


def update_wrong_book_for_exam(db: Session, user_id: int, question_id: int, correct: bool) -> None:
    wrong_record = db.scalar(
        select(UserWrongQuestion).where(
            UserWrongQuestion.user_id == user_id,
            UserWrongQuestion.question_id == question_id,
        )
    )
    if correct:
        if wrong_record:
            wrong_record.last_answer_correct = True
            wrong_record.removed_at = None
        return
    if wrong_record:
        wrong_record.wrong_count += 1
        wrong_record.last_wrong_at = utc_now()
        wrong_record.last_answer_correct = False
        wrong_record.removed_at = None
    else:
        db.add(
            UserWrongQuestion(
                user_id=user_id,
                question_id=question_id,
                wrong_count=1,
                last_wrong_at=utc_now(),
                last_answer_correct=False,
            )
        )


def serialize_exam_record(db: Session, record: ExamRecord, user_id: int | None = None) -> dict:
    return {
        "id": record.id,
        "exam_id": record.exam_id,
        "exam_name": record.exam.name if record.exam else None,
        "user_id": record.user_id,
        "started_at": record.started_at,
        "submitted_at": record.submitted_at,
        "score": record.score,
        "correct_count": record.correct_count,
        "wrong_count": record.wrong_count,
        "status": record.status,
        "answers": [
            {
                "question_id": answer.question_id,
                "answer": answer.answer,
                "is_correct": answer.is_correct,
                "score": answer.score,
                "question": serialize_question(db, answer.question, user_id) if answer.question else None,
            }
            for answer in record.answers
        ],
    }
