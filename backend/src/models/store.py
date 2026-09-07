import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from src.database.connection import Base

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.order import Order

class Store(Base):
    """
    SQLAlchemy 2.x model for Dark Store facilities.
    """
    __tablename__ = "stores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    store_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )
    store_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False
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

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="store")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="store")

    def __repr__(self) -> str:
        return f"<Store(id={self.id}, code='{self.store_code}', name='{self.store_name}')>"
