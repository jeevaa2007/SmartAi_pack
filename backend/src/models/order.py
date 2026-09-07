import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from src.database.connection import Base

if TYPE_CHECKING:
    from src.models.store import Store
    from src.models.user import User
    from src.models.product import Product
    from src.models.packing_verification import PackingVerification

class Order(Base):
    """
    SQLAlchemy 2.x model for Dark Store Packing Orders.
    """
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    operator_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="CREATED",
        nullable=False,
        index=True
    )
    verification_status: Mapped[str] = mapped_column(
        String(20),
        default="UNVERIFIED",
        nullable=False,
        index=True
    )
    packing_score: Mapped[Optional[int]] = mapped_column(
        Integer,
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
    store: Mapped["Store"] = relationship("Store", back_populates="orders")
    operator: Mapped[Optional["User"]] = relationship("User")
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    verifications: Mapped[List["PackingVerification"]] = relationship(
        "PackingVerification",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, number='{self.order_number}', status='{self.status}')>"

class OrderItem(Base):
    """
    SQLAlchemy 2.x model for Line Items within an Order.
    """
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )
    item_attributes_snapshot: Mapped[Optional[str]] = mapped_column(
        Text,
        default="{}",
        nullable=True
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")

    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, qty={self.quantity})>"
