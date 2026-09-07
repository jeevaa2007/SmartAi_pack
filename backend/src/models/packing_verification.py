import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from src.database.connection import Base

if TYPE_CHECKING:
    from src.models.order import Order
    from src.models.user import User
    from src.models.packaging_rule import PackagingRule

class PackingVerification(Base):
    """
    SQLAlchemy 2.x model for Packing Verification Records.
    Persists evaluation results, calculated scores, and outcome statuses.
    """
    __tablename__ = "packing_verifications"

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
    operator_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    image_path: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    packing_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )
    violations_json: Mapped[str] = mapped_column(
        Text,
        default="[]",
        nullable=False
    )
    recommendations_json: Mapped[str] = mapped_column(
        Text,
        default="[]",
        nullable=False
    )
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="verifications")
    operator: Mapped[Optional["User"]] = relationship("User")
    violations: Mapped[List["RuleViolation"]] = relationship(
        "RuleViolation",
        back_populates="verification",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<PackingVerification(id={self.id}, order_id={self.order_id}, score={self.packing_score}, status='{self.status}')>"

class RuleViolation(Base):
    """
    SQLAlchemy 2.x model for Individual Rule Violations detected during verification.
    """
    __tablename__ = "rule_violations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    verification_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("packing_verifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    rule_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("packaging_rules.id", ondelete="SET NULL"),
        nullable=True
    )
    rule_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    rule_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    detected_value: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    expected_value: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    deduction: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    verification: Mapped["PackingVerification"] = relationship("PackingVerification", back_populates="violations")

    def __repr__(self) -> str:
        return f"<RuleViolation(id={self.id}, rule_name='{self.rule_name}', severity='{self.severity}')>"
