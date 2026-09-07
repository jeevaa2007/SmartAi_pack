import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from src.database.connection import Base

class PackagingMaterial(Base):
    """
    SQLAlchemy 2.x model for Packaging Materials (cartons, bubble wrap, ice packs, etc.).
    """
    __tablename__ = "packaging_materials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    material_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    capacity_size: Mapped[str] = mapped_column(
        String(50),
        default="MEDIUM",
        nullable=False
    )
    protection_level: Mapped[str] = mapped_column(
        String(20),
        default="MEDIUM",
        nullable=False
    )
    temperature_suitability: Mapped[str] = mapped_column(
        String(20),
        default="ALL",
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
        return f"<PackagingMaterial(id={self.id}, code='{self.code}', name='{self.name}')>"
