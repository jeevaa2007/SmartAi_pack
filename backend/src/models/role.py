import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from src.database.connection import Base

if TYPE_CHECKING:
    from src.models.user import User

class Role(Base):
    """
    SQLAlchemy 2.x model for security roles.
    Defines permissions hierarchy boundaries (ADMIN, SUPERVISOR, OPERATOR).
    """
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
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

    # 1 -> N Relationship: Role -> Users
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="role",
        passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}', is_active={self.is_active})>"
