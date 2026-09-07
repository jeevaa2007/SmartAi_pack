import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from src.database.connection import Base

class PackagingRule(Base):
    """
    SQLAlchemy 2.x model for Packing Quality Verification Rules.
    Represents declarative business rules for packaging quality validation.
    """
    __tablename__ = "packaging_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    rule_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    rule_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    condition_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
        nullable=False
    )
    required_material_type: Mapped[str] = mapped_column(
        String(50),
        nullable=True
    )
    min_protection_level: Mapped[str] = mapped_column(
        String(20),
        nullable=True
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        default="HIGH",
        nullable=False
    )
    deduction_points: Mapped[int] = mapped_column(
        Integer,
        default=25,
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

    def __repr__(self) -> str:
        return f"<PackagingRule(id={self.id}, code='{self.rule_code}', name='{self.name}')>"
