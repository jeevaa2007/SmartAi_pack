from typing import List, Dict
from pydantic import BaseModel
from src.schemas.order import OrderResponse
from src.schemas.packing_verification import VerificationResponse

class OutcomeBreakdown(BaseModel):
    pass_count: int
    warning_count: int
    fail_count: int

class DashboardStatsResponse(BaseModel):
    total_orders: int
    verified_orders: int
    pass_rate: float
    warning_count: int
    failure_count: int
    avg_packing_score: float
    recent_orders: List[OrderResponse] = []
    recent_verifications: List[VerificationResponse] = []
    outcome_breakdown: OutcomeBreakdown
