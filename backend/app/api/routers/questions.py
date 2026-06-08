from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import FileResponse
from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import db_session, require_admin, get_current_user
from app.core.config import resolve_backend_path, settings
from app.core.exceptions import AppError
from app.db.base import utc_now
from app.models.import_record import ImportRecord
from app.models.practice import UserFavorite
from app.models.question import Question, QuestionTag
from app.models.user import User
from app.schemas.common import MessageOut, PageOut
from app.schemas.question import (
    DuplicateCheckIn,
    DuplicateItemOut,
    ImportConfirmIn,
    ImportPreviewOut,
    ImportRecordOut,
    QuestionBatchIn,
    QuestionCreate,
    QuestionOut,
    QuestionUpdate,
)
from app.services.import_service import confirm_import, generate_template, preview_import
from app.services.log_service import log_operation
from app.services.question_service import create_question, duplicate_candidates, update_question
from app.services.serializers import serialize_question
from app.utils.pagination import paginate

router = APIRouter(tags=["题目"])


def question_query_base():
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


@router.get("/questions", response_model=PageOut)
def list_questions(
    db: Session = Depends(db_session),
    current_user: User | None = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    subject_id: int | None = None,
    chapter_id: int | None = None,
    knowledge_point_id: int | None = None,
    question_type: str | None = None,
    difficulty: str | None = None,
    status: str | None = None,
    source: str | None = None,
    keyword: str | None = None,
    correct_rate_min: float | None = Query(default=None, ge=0, le=100),
    correct_rate_max: float | None = Query(default=None, ge=0, le=100),
    include_deleted: bool = False,
    sort: str = "created_desc",
) -> PageOut:
    stmt = question_query_base()
    if not include_deleted:
        stmt = stmt.where(Question.deleted_at.is_(None))
    if status:
        stmt = stmt.where(Question.status == status)
    else:
        # 学生端默认只看已发布题，管理员可显式传 status 查看其它状态。
        if current_user.role.name == "student":
            stmt = stmt.where(Question.status == "published")
    if subject_id:
        stmt = stmt.where(Question.subject_id == subject_id)
    if chapter_id:
        stmt = stmt.where(Question.chapter_id == chapter_id)
    if knowledge_point_id:
        stmt = stmt.where(Question.knowledge_point_id == knowledge_point_id)
    if question_type:
        stmt = stmt.where(Question.question_type == question_type)
    if difficulty:
        stmt = stmt.where(Question.difficulty == difficulty)
    if source:
        stmt = stmt.where(Question.source == source)
    if keyword:
        stmt = stmt.where(Question.stem.contains(keyword))
    if correct_rate_min is not None:
        stmt = stmt.where(Question.correct_rate >= correct_rate_min)
    if correct_rate_max is not None:
        stmt = stmt.where(Question.correct_rate <= correct_rate_max)
    if sort == "wrong_rate_desc":
        stmt = stmt.order_by((100 - Question.correct_rate).desc(), Question.id.desc())
    elif sort == "correct_rate_asc":
        stmt = stmt.order_by(Question.correct_rate.asc(), Question.id.desc())
    else:
        stmt = stmt.order_by(Question.created_at.desc(), Question.id.desc())
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[serialize_question(db, item, current_user.id, detail=False) for item in items],
    )


@router.get("/questions/{question_id}", response_model=QuestionOut)
def get_question(
    question_id: int,
    db: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    question = db.scalar(question_query_base().where(Question.id == question_id, Question.deleted_at.is_(None)))
    if not question:
        raise AppError("题目不存在", 404)
    if current_user.role.name == "student" and question.status != "published":
        raise AppError("题目未发布", 403)
    return serialize_question(db, question, current_user.id)


@router.post("/admin/questions", response_model=QuestionOut)
def admin_create_question(
    payload: QuestionCreate,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> dict:
    question = create_question(db, payload, admin)
    log_operation(db, admin, "create_question", "question", f"新增题目：{question.stem[:60]}", question.id)
    db.commit()
    question = db.scalar(question_query_base().where(Question.id == question.id))
    return serialize_question(db, question, admin.id)


@router.put("/admin/questions/{question_id}", response_model=QuestionOut)
def admin_update_question(
    question_id: int,
    payload: QuestionUpdate,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> dict:
    question = db.scalar(question_query_base().where(Question.id == question_id, Question.deleted_at.is_(None)))
    if not question:
        raise AppError("题目不存在", 404)
    update_question(db, question, payload)
    log_operation(db, admin, "update_question", "question", f"编辑题目：{question.stem[:60]}", question.id)
    db.commit()
    question = db.scalar(question_query_base().where(Question.id == question_id))
    return serialize_question(db, question, admin.id)


@router.delete("/admin/questions/{question_id}", response_model=MessageOut)
def admin_delete_question(
    question_id: int,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    question = db.get(Question, question_id)
    if question and not question.deleted_at:
        question.deleted_at = utc_now()
        log_operation(db, admin, "delete_question", "question", f"软删除题目：{question.stem[:60]}", question.id)
        db.commit()
    return MessageOut(message="题目已移入回收站")


@router.post("/admin/questions/{question_id}/restore", response_model=MessageOut)
def admin_restore_question(
    question_id: int,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    question = db.get(Question, question_id)
    if not question:
        raise AppError("题目不存在", 404)
    question.deleted_at = None
    log_operation(db, admin, "restore_question", "question", f"恢复题目：{question.stem[:60]}", question.id)
    db.commit()
    return MessageOut(message="题目已恢复")


@router.delete("/admin/questions/{question_id}/hard", response_model=MessageOut)
def admin_hard_delete_question(
    question_id: int,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    question = db.get(Question, question_id)
    if question:
        summary = question.stem[:60]
        db.delete(question)
        log_operation(db, admin, "hard_delete_question", "question", f"彻底删除题目：{summary}", question_id)
        db.commit()
    return MessageOut(message="题目已彻底删除")


@router.post("/admin/questions/batch", response_model=MessageOut)
def admin_batch_questions(
    payload: QuestionBatchIn,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    questions = db.scalars(select(Question).where(Question.id.in_(payload.ids))).all()
    for question in questions:
        if payload.action == "publish":
            question.status = "published"
        elif payload.action == "offline":
            question.status = "offline"
        elif payload.action == "delete":
            question.deleted_at = utc_now()
        elif payload.action == "change_taxonomy":
            if payload.subject_id:
                question.subject_id = payload.subject_id
            if payload.chapter_id:
                question.chapter_id = payload.chapter_id
            if payload.knowledge_point_id:
                question.knowledge_point_id = payload.knowledge_point_id
        elif payload.action == "change_difficulty" and payload.difficulty:
            question.difficulty = payload.difficulty
        elif payload.action == "tag" and payload.tags:
            existing = {tag.tag for tag in question.tags}
            for tag in payload.tags:
                if tag not in existing:
                    db.add(QuestionTag(question_id=question.id, tag=tag))
        else:
            raise AppError("不支持的批量操作")
    log_operation(db, admin, f"batch_{payload.action}", "question", f"批量操作题目：{payload.ids}")
    db.commit()
    return MessageOut(message="批量操作已完成")


@router.post("/admin/questions/check-duplicate", response_model=list[DuplicateItemOut])
def admin_check_duplicate(
    payload: DuplicateCheckIn,
    db: Session = Depends(db_session),
    _: User = Depends(require_admin),
) -> list[dict]:
    return duplicate_candidates(db, payload.stem, payload.threshold)


@router.get("/admin/questions/import/template")
def download_import_template(_: User = Depends(require_admin)):
    path = generate_template()
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="医学刷题题目导入模板.xlsx",
    )


@router.post("/admin/questions/import/preview", response_model=ImportPreviewOut)
async def admin_import_preview(
    file: UploadFile = File(...),
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> ImportPreviewOut:
    if not file.filename or not file.filename.endswith(".xlsx"):
        raise AppError("请上传 .xlsx 文件")
    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise AppError(f"文件不能超过 {settings.max_upload_size_mb}MB")
    upload_dir = resolve_backend_path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_path = upload_dir / f"question_import_{uuid4().hex}.xlsx"
    saved_path.write_bytes(content)
    record = preview_import(db, saved_path, file.filename, admin)
    log_operation(db, admin, "preview_question_import", "import_record", f"预览导入文件：{file.filename}", record.id)
    db.commit()
    summary = record.summary_json

    data = json.loads(summary or "{}")
    return ImportPreviewOut(
        import_record_id=record.id,
        total_count=record.total_count,
        valid_count=data.get("valid_count", 0),
        failed_count=record.failed_count,
        duplicate_count=record.duplicate_count,
        rows=data.get("rows", []),
    )


@router.post("/admin/questions/import", response_model=ImportPreviewOut)
async def admin_import_preview_alias(
    file: UploadFile = File(...),
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> ImportPreviewOut:
    return await admin_import_preview(file=file, db=db, admin=admin)


@router.post("/admin/questions/import/confirm", response_model=ImportRecordOut)
def admin_import_confirm(
    payload: ImportConfirmIn,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> ImportRecord:
    record = db.get(ImportRecord, payload.import_record_id)
    if not record:
        raise AppError("导入记录不存在", 404)
    if record.status == "completed":
        raise AppError("该导入记录已确认过")
    confirm_import(
        db,
        record,
        admin,
        payload.auto_create_taxonomy,
        payload.skip_duplicates,
        [item.model_dump() for item in payload.taxonomy_mappings],
    )
    log_operation(db, admin, "confirm_question_import", "import_record", f"确认导入：{record.file_name}", record.id)
    db.commit()
    db.refresh(record)
    return record


@router.get("/admin/questions/import/records", response_model=PageOut)
def admin_import_records(
    db: Session = Depends(db_session),
    _: User = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
) -> PageOut:
    stmt = select(ImportRecord).where(ImportRecord.deleted_at.is_(None)).order_by(ImportRecord.created_at.desc())
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(total=total, page=page, page_size=page_size, items=items)


@router.get("/admin/questions/import/records/{record_id}")
def admin_import_record_detail(
    record_id: int,
    db: Session = Depends(db_session),
    _: User = Depends(require_admin),
) -> dict:
    record = db.get(ImportRecord, record_id)
    if not record or record.deleted_at:
        raise AppError("导入记录不存在", 404)
    return {
        "id": record.id,
        "file_name": record.file_name,
        "status": record.status,
        "total_count": record.total_count,
        "success_count": record.success_count,
        "failed_count": record.failed_count,
        "skipped_count": record.skipped_count,
        "duplicate_count": record.duplicate_count,
        "error_report_path": record.error_report_path,
        "summary": json.loads(record.summary_json or "{}"),
        "created_at": record.created_at,
    }


@router.get("/admin/questions/import/records/{record_id}/error-report")
def admin_import_error_report(
    record_id: int,
    db: Session = Depends(db_session),
    _: User = Depends(require_admin),
) -> FileResponse:
    record = db.get(ImportRecord, record_id)
    if not record or not record.error_report_path:
        raise AppError("错误报告不存在", 404)
    path = Path(record.error_report_path)
    if not path.exists():
        raise AppError("错误报告文件不存在", 404)
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"导入错误报告_{record.id}.xlsx",
    )


@router.get("/admin/questions/export")
def admin_export_questions(
    db: Session = Depends(db_session),
    _: User = Depends(require_admin),
    subject_id: int | None = None,
    chapter_id: int | None = None,
    knowledge_point_id: int | None = None,
    status: str | None = None,
) -> FileResponse:
    stmt = question_query_base().where(Question.deleted_at.is_(None))
    if subject_id:
        stmt = stmt.where(Question.subject_id == subject_id)
    if chapter_id:
        stmt = stmt.where(Question.chapter_id == chapter_id)
    if knowledge_point_id:
        stmt = stmt.where(Question.knowledge_point_id == knowledge_point_id)
    if status:
        stmt = stmt.where(Question.status == status)
    questions = db.scalars(stmt.order_by(Question.id.asc())).all()
    wb = Workbook()
    ws = wb.active
    ws.title = "题目导出"
    ws.append(["ID", "题型", "题干", "选项A", "选项B", "选项C", "选项D", "选项E", "正确答案", "解析", "科目", "章节", "知识点", "难度", "重要程度", "来源", "年份", "标签", "状态"])
    for question in questions:
        option_map = {option.option_key: option.content for option in question.options}
        ws.append(
            [
                question.id,
                question.question_type,
                question.stem,
                option_map.get("A", ""),
                option_map.get("B", ""),
                option_map.get("C", ""),
                option_map.get("D", ""),
                option_map.get("E", ""),
                question.correct_answer,
                question.analysis,
                question.subject.name if question.subject else "",
                question.chapter.name if question.chapter else "",
                question.knowledge_point.name if question.knowledge_point else "",
                question.difficulty,
                question.importance,
                question.source,
                question.year,
                ",".join(tag.tag for tag in question.tags),
                question.status,
            ]
        )
    export_dir = resolve_backend_path(settings.upload_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    path = export_dir / f"question_export_{uuid4().hex}.xlsx"
    wb.save(path)
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="医学刷题题目导出.xlsx",
    )


@router.post("/admin/upload/image")
async def admin_upload_image(
    file: UploadFile = File(...),
    _: User = Depends(require_admin),
) -> dict:
    allowed = {"image/png", "image/jpeg", "image/webp", "image/gif"}
    if file.content_type not in allowed:
        raise AppError("仅支持 png、jpg、webp、gif 图片")
    content = await file.read()
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise AppError(f"图片不能超过 {settings.max_upload_size_mb}MB")
    suffix = Path(file.filename or "image.png").suffix.lower() or ".png"
    upload_dir = resolve_backend_path(settings.upload_dir) / "images"
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"{uuid4().hex}{suffix}"
    path.write_bytes(content)
    return {"url": f"/uploads/images/{path.name}", "file_name": path.name, "size": len(content)}
