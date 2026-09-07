import uuid
from typing import Optional
from sqlalchemy.orm import Session
from src.models.audit_log import AuditLog

class AuditRepository:
    """
    Data repository handling AuditLog event recording.
    """

    @staticmethod
    def create_audit_entry(
        db: Session,
        user_id: Optional[uuid.UUID],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> AuditLog:
        """
        Persists an immutable audit trail entry recording security and domain actions.
        """
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            ip_address=ip_address,
            request_id=request_id
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry
