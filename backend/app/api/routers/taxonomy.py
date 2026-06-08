from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import db_session, require_admin
from app.core.exceptions import AppError
from app.db.base import utc_now
from app.models.taxonomy import Chapter, KnowledgePoint, Subject
from app.models.user import User
from app.schemas.common import MessageOut, PageOut
from app.schemas.taxonomy import (
    ChapterBatchStatusIn,
    ChapterCreate,
    ChapterOut,
    ChapterUpdate,
    KnowledgePointCreate,
    KnowledgePointImportItem,
    KnowledgePointOut,
    KnowledgePointUpdate,
    ReorderItem,
    SubjectCreate,
    SubjectOut,
    SubjectUpdate,
)
from app.services.log_service import log_operation
from app.services.serializers import serialize_chapter, serialize_knowledge_point, serialize_subject
from app.utils.pagination import paginate

router = APIRouter(tags=["题库分类"])


@router.get("/subjects", response_model=PageOut)
def list_subjects(
    db: Session = Depends(db_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
    keyword: str | None = None,
    enabled: bool | None = None,
) -> PageOut:
    stmt = select(Subject).where(Subject.deleted_at.is_(None))
    if keyword:
        stmt = stmt.where(Subject.name.contains(keyword))
    if enabled is not None:
        stmt = stmt.where(Subject.is_enabled == enabled)
    stmt = stmt.order_by(Subject.sort_order.asc(), Subject.id.asc())
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(total=total, page=page, page_size=page_size, items=[serialize_subject(db, item) for item in items])


@router.post("/admin/subjects", response_model=SubjectOut)
def create_subject(
    payload: SubjectCreate,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> dict:
    subject = Subject(**payload.model_dump())
    db.add(subject)
    db.flush()
    log_operation(db, admin, "create_subject", "subject", f"新增科目：{subject.name}", subject.id)
    db.commit()
    db.refresh(subject)
    return serialize_subject(db, subject)


@router.put("/admin/subjects/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> dict:
    subject = db.get(Subject, subject_id)
    if not subject or subject.deleted_at:
        raise AppError("科目不存在", 404)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(subject, key, value)
    log_operation(db, admin, "update_subject", "subject", f"编辑科目：{subject.name}", subject.id)
    db.commit()
    db.refresh(subject)
    return serialize_subject(db, subject)


@router.delete("/admin/subjects/{subject_id}", response_model=MessageOut)
def delete_subject(
    subject_id: int,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    subject = db.get(Subject, subject_id)
    if subject and not subject.deleted_at:
        subject.deleted_at = utc_now()
        log_operation(db, admin, "delete_subject", "subject", f"删除科目：{subject.name}", subject.id)
        db.commit()
    return MessageOut(message="已删除科目")


@router.post("/admin/subjects/reorder", response_model=MessageOut)
def reorder_subjects(
    payload: list[ReorderItem],
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    for item in payload:
        subject = db.get(Subject, item.id)
        if subject and not subject.deleted_at:
            subject.sort_order = item.sort_order
    log_operation(db, admin, "reorder_subjects", "subject", "调整科目排序")
    db.commit()
    return MessageOut(message="排序已保存")


@router.get("/chapters", response_model=PageOut)
def list_chapters(
    db: Session = Depends(db_session),
    subject_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
    keyword: str | None = None,
    enabled: bool | None = None,
) -> PageOut:
    stmt = select(Chapter).options(selectinload(Chapter.subject)).where(Chapter.deleted_at.is_(None))
    if subject_id:
        stmt = stmt.where(Chapter.subject_id == subject_id)
    if keyword:
        stmt = stmt.where(Chapter.name.contains(keyword))
    if enabled is not None:
        stmt = stmt.where(Chapter.is_enabled == enabled)
    stmt = stmt.order_by(Chapter.sort_order.asc(), Chapter.id.asc())
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(total=total, page=page, page_size=page_size, items=[serialize_chapter(db, item) for item in items])


@router.post("/admin/chapters", response_model=ChapterOut)
def create_chapter(
    payload: ChapterCreate,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> dict:
    chapter = Chapter(**payload.model_dump())
    db.add(chapter)
    db.flush()
    log_operation(db, admin, "create_chapter", "chapter", f"新增章节：{chapter.name}", chapter.id)
    db.commit()
    db.refresh(chapter)
    return serialize_chapter(db, chapter)


@router.put("/admin/chapters/{chapter_id}", response_model=ChapterOut)
def update_chapter(
    chapter_id: int,
    payload: ChapterUpdate,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> dict:
    chapter = db.get(Chapter, chapter_id)
    if not chapter or chapter.deleted_at:
        raise AppError("章节不存在", 404)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(chapter, key, value)
    log_operation(db, admin, "update_chapter", "chapter", f"编辑章节：{chapter.name}", chapter.id)
    db.commit()
    db.refresh(chapter)
    return serialize_chapter(db, chapter)


@router.delete("/admin/chapters/{chapter_id}", response_model=MessageOut)
def delete_chapter(
    chapter_id: int,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    chapter = db.get(Chapter, chapter_id)
    if chapter and not chapter.deleted_at:
        chapter.deleted_at = utc_now()
        log_operation(db, admin, "delete_chapter", "chapter", f"删除章节：{chapter.name}", chapter.id)
        db.commit()
    return MessageOut(message="已删除章节")


@router.post("/admin/chapters/batch-status", response_model=MessageOut)
def batch_chapter_status(
    payload: ChapterBatchStatusIn,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    for chapter in db.scalars(select(Chapter).where(Chapter.id.in_(payload.ids))).all():
        chapter.is_enabled = payload.is_enabled
    log_operation(db, admin, "batch_chapter_status", "chapter", f"批量修改章节状态：{payload.ids}")
    db.commit()
    return MessageOut(message="章节状态已更新")


@router.post("/admin/chapters/reorder", response_model=MessageOut)
def reorder_chapters(
    payload: list[ReorderItem],
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    for item in payload:
        chapter = db.get(Chapter, item.id)
        if chapter and not chapter.deleted_at:
            chapter.sort_order = item.sort_order
    log_operation(db, admin, "reorder_chapters", "chapter", "调整章节排序")
    db.commit()
    return MessageOut(message="章节排序已保存")


@router.get("/knowledge-points", response_model=PageOut)
def list_knowledge_points(
    db: Session = Depends(db_session),
    subject_id: int | None = None,
    chapter_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
    keyword: str | None = None,
    enabled: bool | None = None,
) -> PageOut:
    stmt = (
        select(KnowledgePoint)
        .options(selectinload(KnowledgePoint.subject), selectinload(KnowledgePoint.chapter))
        .where(KnowledgePoint.deleted_at.is_(None))
    )
    if subject_id:
        stmt = stmt.where(KnowledgePoint.subject_id == subject_id)
    if chapter_id:
        stmt = stmt.where(KnowledgePoint.chapter_id == chapter_id)
    if keyword:
        stmt = stmt.where(KnowledgePoint.name.contains(keyword))
    if enabled is not None:
        stmt = stmt.where(KnowledgePoint.is_enabled == enabled)
    stmt = stmt.order_by(KnowledgePoint.sort_order.asc(), KnowledgePoint.id.asc())
    total, items = paginate(db, stmt, page, page_size)
    return PageOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[serialize_knowledge_point(db, item) for item in items],
    )


@router.post("/admin/knowledge-points", response_model=KnowledgePointOut)
def create_knowledge_point(
    payload: KnowledgePointCreate,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> dict:
    kp = KnowledgePoint(**payload.model_dump())
    db.add(kp)
    db.flush()
    log_operation(db, admin, "create_knowledge_point", "knowledge_point", f"新增知识点：{kp.name}", kp.id)
    db.commit()
    db.refresh(kp)
    return serialize_knowledge_point(db, kp)


@router.put("/admin/knowledge-points/{kp_id}", response_model=KnowledgePointOut)
def update_knowledge_point(
    kp_id: int,
    payload: KnowledgePointUpdate,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> dict:
    kp = db.get(KnowledgePoint, kp_id)
    if not kp or kp.deleted_at:
        raise AppError("知识点不存在", 404)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(kp, key, value)
    log_operation(db, admin, "update_knowledge_point", "knowledge_point", f"编辑知识点：{kp.name}", kp.id)
    db.commit()
    db.refresh(kp)
    return serialize_knowledge_point(db, kp)


@router.delete("/admin/knowledge-points/{kp_id}", response_model=MessageOut)
def delete_knowledge_point(
    kp_id: int,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    kp = db.get(KnowledgePoint, kp_id)
    if kp and not kp.deleted_at:
        kp.deleted_at = utc_now()
        log_operation(db, admin, "delete_knowledge_point", "knowledge_point", f"删除知识点：{kp.name}", kp.id)
        db.commit()
    return MessageOut(message="已删除知识点")


@router.post("/admin/knowledge-points/import", response_model=MessageOut)
def import_knowledge_points(
    payload: list[KnowledgePointImportItem],
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    created = 0
    for item in payload:
        subject = db.scalar(select(Subject).where(Subject.name == item.subject_name, Subject.deleted_at.is_(None)))
        if not subject:
            continue
        chapter = db.scalar(
            select(Chapter).where(
                Chapter.subject_id == subject.id,
                Chapter.name == item.chapter_name,
                Chapter.deleted_at.is_(None),
            )
        )
        if not chapter:
            continue
        exists = db.scalar(
            select(KnowledgePoint).where(
                KnowledgePoint.chapter_id == chapter.id,
                KnowledgePoint.name == item.name,
                KnowledgePoint.deleted_at.is_(None),
            )
        )
        if exists:
            continue
        db.add(
            KnowledgePoint(
                subject_id=subject.id,
                chapter_id=chapter.id,
                name=item.name,
                label=item.label,
                importance_level=item.importance_level,
                description=item.description,
            )
        )
        created += 1
    log_operation(db, admin, "import_knowledge_points", "knowledge_point", f"批量导入知识点 {created} 个")
    db.commit()
    return MessageOut(message=f"已导入 {created} 个知识点")


@router.post("/admin/knowledge-points/reorder", response_model=MessageOut)
def reorder_knowledge_points(
    payload: list[ReorderItem],
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> MessageOut:
    for item in payload:
        kp = db.get(KnowledgePoint, item.id)
        if kp and not kp.deleted_at:
            kp.sort_order = item.sort_order
    log_operation(db, admin, "reorder_knowledge_points", "knowledge_point", "调整知识点排序")
    db.commit()
    return MessageOut(message="知识点排序已保存")
