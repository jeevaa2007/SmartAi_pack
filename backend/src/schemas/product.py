import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    sku: str = Field(..., max_length=50, example="SKU-GLS-1001")
    name: str = Field(..., max_length=255, example="Organic Whole Milk 1L (Glass Bottle)")
    category: str = Field(..., max_length=100, example="Dairy & Eggs")
    weight: float = Field(..., ge=0.0, example=1.05)
    dimensions: Optional[str] = Field(None, example="10x10x25 cm")
    is_fragile: bool = False
    temperature_req: str = Field("AMBIENT", example="COLD") # AMBIENT, COLD, FROZEN
    is_liquid: bool = False
    is_crush_sensitive: bool = False
    preferred_packaging_type: Optional[str] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    is_fragile: Optional[bool] = None
    temperature_req: Optional[str] = None
    is_liquid: Optional[bool] = None
    is_crush_sensitive: Optional[bool] = None
    preferred_packaging_type: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
