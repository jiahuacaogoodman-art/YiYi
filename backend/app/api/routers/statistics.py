from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user, require_admin
from app.db.base import utc_now
from app.models.feedback import QuestionFeedback
from app.models.import_record import ImportRecord
from app.models.log import OperationLog
from app.models.practice import UserAnswer, UserWrongQuestion
from app.models.question import Question
from app.models.taxonomy import Chapter, KnowledgePoint, Subject
from app.models.user import User
from app.schemas.statistics import DashboardStatisticsOut, UserStatisticsOut

router = APIRouter(tags=["统计"])


@router.get("/statistics/user", response_model=UserStatisticsOut)
def user_statistics(
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> UserStatisticsOut:
    total = db.scalar(select(func.count(UserAnswer.id)).where(UserAnswer.user_id == current_user.id)) or 0
    correct = db.scalar(
        select(func.count(UserAnswer.id)).where(UserAnswer.user_id == current_user.id, UserAnswer.is_correct.is_(True))
    ) or 0
    wrong = total - correct
    subject_rows = db.execute(
        select(
            Subject.id,
            Subject.name,
            func.count(UserAnswer.id).label("total"),
            func.sum(case((UserAnswer.is_correct.is_(True), 1), else_=0)).label("correct"),
        )
        .join(Question, Question.subject_id == Subject.id)
        .join(UserAnswer, UserAnswer.question_id == Question.id)
        .where(UserAnswer.user_id == current_user.id)
        .group_by(Subject.id, Subject.name)
    ).all()
    chapter_rows = db.execute(
        select(
            Chapter.id,
            Chapter.name,
            func.count(UserAnswer.id).label("total"),
            func.sum(case((UserAnswer.is_correct.is_(True), 1), else_=0)).label("correct"),
        )
        .join(Question, Question.chapter_id == Chapter.id)
        .join(UserAnswer, UserAnswer.question_id == Question.id)
        .where(UserAnswer.user_id == current_user.id)
        .group_by(Chapter.id, Chapter.name)
    ).all()
    start_day = utc_now().date() - timedelta(days=6)
    trend_rows = db.execute(
        select(
            func.date(UserAnswer.created_at).label("day"),
            func.count(UserAnswer.id).label("total"),
            func.sum(case((UserAnswer.is_correct.is_(True), 1), else_=0)).label("correct"),
        )
        .where(UserAnswer.user_id == current_user.id, UserAnswer.created_at >= start_day)
        .group_by(func.date(UserAnswer.created_at))
        .order_by(func.date(UserAnswer.created_at))
    ).all()
    wrong_point_rows = db.execute(
        select(
            KnowledgePoint.id,
            KnowledgePoint.name,
            func.sum(UserWrongQuestion.wrong_count).label("wrong_count"),
        )
        .join(Question, Question.knowledge_point_id == KnowledgePoint.id)
        .join(UserWrongQuestion, UserWrongQuestion.question_id == Question.id)
        .where(UserWrongQuestion.user_id == current_user.id, UserWrongQuestion.deleted_at.is_(None))
        .group_by(KnowledgePoint.id, KnowledgePoint.name)
        .order_by(func.sum(UserWrongQuestion.wrong_count).desc())
        .limit(10)
    ).all()
    recommended = [
        {"chapter_id": row.id, "chapter_name": row.name, "mastery": accuracy(row.correct, row.total)}
        for row in sorted(chapter_rows, key=lambda item: accuracy(item.correct, item.total))[:5]
    ]
    return UserStatisticsOut(
        total_answers=total,
        correct_count=correct,
        wrong_count=wrong,
        correct_rate=accuracy(correct, total),
        subject_accuracy=[
            {
                "subject_id": row.id,
                "subject_name": row.name,
                "total": row.total,
                "correct": int(row.correct or 0),
                "correct_rate": accuracy(row.correct, row.total),
            }
            for row in subject_rows
        ],
        chapter_mastery=[
            {
                "chapter_id": row.id,
                "chapter_name": row.name,
                "total": row.total,
                "correct": int(row.correct or 0),
                "mastery": accuracy(row.correct, row.total),
            }
            for row in chapter_rows
        ],
        recent_7_days=[
            {
                "date": str(row.day),
                "total": row.total,
                "correct": int(row.correct or 0),
                "correct_rate": accuracy(row.correct, row.total),
            }
            for row in trend_rows
        ],
        high_frequency_wrong_points=[
            {"knowledge_point_id": row.id, "knowledge_point_name": row.name, "wrong_count": int(row.wrong_count or 0)}
            for row in wrong_point_rows
        ],
        recommended_chapters=recommended,
    )


@router.get("/admin/statistics/dashboard", response_model=DashboardStatisticsOut)
def admin_dashboard(
    db: Session = Depends(db_session),
    _: User = Depends(require_admin),
) -> DashboardStatisticsOut:
    today = utc_now().date()
    total_questions = db.scalar(select(func.count(Question.id)).where(Question.deleted_at.is_(None))) or 0
    published = db.scalar(select(func.count(Question.id)).where(Question.status == "published", Question.deleted_at.is_(None))) or 0
    draft = db.scalar(select(func.count(Question.id)).where(Question.status == "draft", Question.deleted_at.is_(None))) or 0
    pending = db.scalar(select(func.count(Question.id)).where(Question.status == "pending_review", Question.deleted_at.is_(None))) or 0
    today_new = db.scalar(select(func.count(Question.id)).where(Question.created_at >= today, Question.deleted_at.is_(None))) or 0
    total_users = db.scalar(select(func.count(User.id)).where(User.deleted_at.is_(None))) or 0
    today_practice = db.scalar(select(func.count(UserAnswer.id)).where(UserAnswer.created_at >= today)) or 0
    feedback_count = db.scalar(select(func.count(QuestionFeedback.id)).where(QuestionFeedback.deleted_at.is_(None))) or 0
    subject_distribution_rows = db.execute(
        select(Subject.id, Subject.name, func.count(Question.id).label("count"))
        .join(Question, Question.subject_id == Subject.id, isouter=True)
        .where(Subject.deleted_at.is_(None))
        .group_by(Subject.id, Subject.name)
        .order_by(func.count(Question.id).desc())
    ).all()
    trend_rows = db.execute(
        select(func.date(UserAnswer.created_at).label("day"), func.count(UserAnswer.id).label("count"))
        .where(UserAnswer.created_at >= today - timedelta(days=6))
        .group_by(func.date(UserAnswer.created_at))
        .order_by(func.date(UserAnswer.created_at))
    ).all()
    wrong_rows = db.execute(
        select(
            KnowledgePoint.id,
            KnowledgePoint.name,
            func.sum(Question.wrong_count).label("wrong_count"),
            func.sum(Question.practice_count).label("practice_count"),
        )
        .join(Question, Question.knowledge_point_id == KnowledgePoint.id)
        .where(Question.deleted_at.is_(None))
        .group_by(KnowledgePoint.id, KnowledgePoint.name)
        .order_by(func.sum(Question.wrong_count).desc())
        .limit(10)
    ).all()
    imports = db.scalars(select(ImportRecord).order_by(ImportRecord.created_at.desc()).limit(10)).all()
    logs = db.scalars(select(OperationLog).order_by(OperationLog.created_at.desc()).limit(10)).all()
    return DashboardStatisticsOut(
        total_questions=total_questions,
        published_questions=published,
        draft_questions=draft,
        pending_review_questions=pending,
        today_new_questions=today_new,
        total_users=total_users,
        today_practice_count=today_practice,
        feedback_count=feedback_count,
        subject_distribution=[
            {"subject_id": row.id, "subject_name": row.name, "question_count": row.count}
            for row in subject_distribution_rows
        ],
        user_practice_trend=[{"date": str(row.day), "count": row.count} for row in trend_rows],
        top_wrong_knowledge_points=[
            {
                "knowledge_point_id": row.id,
                "knowledge_point_name": row.name,
                "wrong_count": int(row.wrong_count or 0),
                "wrong_rate": round((row.wrong_count or 0) / row.practice_count * 100, 2) if row.practice_count else 0,
            }
            for row in wrong_rows
        ],
        recent_import_records=[
            {
                "id": record.id,
                "file_name": record.file_name,
                "status": record.status,
                "success_count": record.success_count,
                "failed_count": record.failed_count,
                "created_at": record.created_at,
            }
            for record in imports
        ],
        recent_operation_logs=[
            {
                "id": log.id,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "summary": log.summary,
                "created_at": log.created_at,
            }
            for log in logs
        ],
    )


def accuracy(correct: int | None, total: int | None) -> float:
    if not total:
        return 0
    return round((correct or 0) / total * 100, 2)

