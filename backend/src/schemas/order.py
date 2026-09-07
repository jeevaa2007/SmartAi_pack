import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from src.schemas.product import ProductResponse

class OrderItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(1, ge=1)

class OrderItemResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    item_attributes_snapshot: Optional[str] = "{}"
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    store_id: uuid.UUID
    operator_id: Optional[uuid.UUID] = None
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: uuid.UUID
    order_number: str
    store_id: uuid.UUID
    store_code: Optional[str] = None
    store_name: Optional[str] = None
    operator_id: Optional[uuid.UUID] = None
    operator_name: Optional[str] = None
    status: str
    verification_status: str
    packing_score: Optional[int] = None
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
