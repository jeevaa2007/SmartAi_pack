import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class StoreBase(BaseModel):
    store_code: str = Field(..., max_length=30, example="STR-BLR-001")
    store_name: str = Field(..., max_length=100, example="Indiranagar Dark Store")
    location: str = Field(..., max_length=255, example="Bangalore, KA")
    is_active: bool = True

class StoreCreate(StoreBase):
    pass

class StoreUpdate(BaseModel):
    store_code: Optional[str] = None
    store_name: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None

class StoreResponse(StoreBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
