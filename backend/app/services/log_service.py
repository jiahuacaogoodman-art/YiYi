from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.log import OperationLog
from app.models.user import User


def log_operation(
    db: Session,
    operator: User | None,
    action: str,
    target_type: str,
    summary: str,
    target_id: str | int | None = None,
    ip_address: str | None = None,
) -> None:
    db.add(
        OperationLog(
            operator_id=operator.id if operator else None,
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            summary=summary,
            ip_address=ip_address,
        )
    )

