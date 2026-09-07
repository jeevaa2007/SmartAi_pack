import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.dialects.postgresql import UUID
from src.database.connection import Base

if TYPE_CHECKING:
    from src.models.role import Role
    from src.models.audit_log import AuditLog

class User(Base):
    """
    SQLAlchemy 2.x model for application users.
    Enforces normalized email storage, bcrypt password hash persistence, and role linkage.
    
    NOTE: store_id is currently a nullable UUID without a Foreign Key constraint because
    the Store model is planned for a future sprint.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    # Store entity dependency placeholder - nullable, no FK until Store model is implemented
    store_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stores.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="users"
    )
    store: Mapped[Optional["Store"]] = relationship(
        "Store",
        back_populates="users"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        passive_deletes=True
    )

    @validates("email")
    def validate_and_normalize_email(self, key: str, address: str) -> str:
        """
        Normalizes email by trimming surrounding whitespace and converting to lowercase
        prior to model persistence.
        """
        if not address:
            raise ValueError("Email address cannot be empty.")
        normalized = address.strip().lower()
        return normalized

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role_id={self.role_id})>"
