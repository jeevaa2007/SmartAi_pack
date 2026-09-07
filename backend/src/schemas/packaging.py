import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class PackagingMaterialBase(BaseModel):
    code: str = Field(..., max_length=50, example="MAT-BUBBLE-01")
    name: str = Field(..., max_length=100, example="Bubble Wrap Cushioning")
    material_type: str = Field(..., max_length=50, example="BUBBLE_WRAP")
    capacity_size: str = Field("MEDIUM", max_length=50, example="MEDIUM")
    protection_level: str = Field("MEDIUM", max_length=20, example="HIGH")
    temperature_suitability: str = Field("ALL", max_length=20, example="ALL")
    is_active: bool = True

class PackagingMaterialCreate(PackagingMaterialBase):
    pass

class PackagingMaterialResponse(PackagingMaterialBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

class PackagingRuleBase(BaseModel):
    rule_code: str = Field(..., max_length=50, example="RULE-FRAGILE-01")
    name: str = Field(..., max_length=100, example="Fragile Cushioning Mandatory")
    description: str = Field(..., example="Fragile items require protective bubble wrap or sleeve.")
    rule_type: str = Field(..., max_length=50, example="FRAGILE_PROTECTION")
    condition_json: str = "{}"
    required_material_type: Optional[str] = None
    min_protection_level: Optional[str] = None
    severity: str = Field("HIGH", example="HIGH") # CRITICAL, HIGH, MEDIUM, LOW
    deduction_points: int = Field(25, ge=0, le=100, example=25)
    is_active: bool = True

class PackagingRuleCreate(PackagingRuleBase):
    pass

class PackagingRuleResponse(PackagingRuleBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
