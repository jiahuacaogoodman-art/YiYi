from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session


def paginate(db: Session, stmt: Select, page: int = 1, page_size: int = 20) -> tuple[int, list]:
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
    return total, items

