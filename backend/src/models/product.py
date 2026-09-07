import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Boolean, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from src.database.connection import Base

if TYPE_CHECKING:
    from src.models.order import OrderItem

class Product(Base):
    """
    SQLAlchemy 2.x model for Catalog Products.
    Stores physical attributes required for packing quality verification.
    """
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    sku: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    weight: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False
    )
    dimensions: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    is_fragile: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    temperature_req: Mapped[str] = mapped_column(
        String(20),
        default="AMBIENT",
        nullable=False
    )
    is_liquid: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    is_crush_sensitive: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    preferred_packaging_type: Mapped[Optional[str]] = mapped_column(
        String(100),
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

    # Relationships
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="product")

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"
