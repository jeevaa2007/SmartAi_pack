import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class RuleViolationResponse(BaseModel):
    id: Optional[uuid.UUID] = None
    rule_code: Optional[str] = None
    rule_name: str
    severity: str
    description: str
    detected_value: Optional[str] = None
    expected_value: Optional[str] = None
    deduction: int = 0

    class Config:
        from_attributes = True

class VerificationRequest(BaseModel):
    order_id: uuid.UUID
    packaging_material_ids: List[uuid.UUID] = Field(..., description="Selected packaging materials used for this order")
    image_path: Optional[str] = Field(None, description="Path to uploaded packing image")

class VerificationResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    order_number: Optional[str] = None
    operator_id: Optional[uuid.UUID] = None
    operator_name: Optional[str] = None
    image_path: Optional[str] = None
    packing_score: int
    status: str # PASS, WARNING, FAIL
    violations: List[RuleViolationResponse] = []
    recommendations: List[str] = []
    verified_at: datetime

    class Config:
        from_attributes = True
