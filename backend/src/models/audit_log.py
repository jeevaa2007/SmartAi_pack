import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from src.database.connection import Base

if TYPE_CHECKING:
    from src.models.user import User

class AuditLog(Base):
    """
    SQLAlchemy 2.x model for security and application audit trail records.
    Audit log entries are immutable. user_id is nullable (ondelete="SET NULL") so that
    security events prior to authentication or after user deletion are preserved.
    """
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    resource_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True
    )
    request_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # N -> 1 Relationship: AuditLog -> User
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="audit_logs"
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"
