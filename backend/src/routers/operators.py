import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from src.database.connection import get_db
from src.schemas.response import APIResponse
from src.api.deps import require_roles
from src.models.user import User
from src.models.role import Role
from src.models.store import Store
from src.models.packing_verification import PackingVerification

router = APIRouter(prefix="/operators", tags=["Operator Performance & Roster"])

class OperatorPerformanceResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    role_name: str
    store_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    last_login_at: Optional[str] = None
    total_verifications: int = 0
    avg_packing_score: float = 0.0

    class Config:
        from_attributes = True

@router.get("", response_model=APIResponse[List[OperatorPerformanceResponse]])
def list_operators(
    store_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR", "OPERATOR"]))
):
    query = db.query(User).options(
        joinedload(User.role),
        joinedload(User.store)
    )
    if store_id:
        query = query.filter(User.store_id == store_id)

    users = query.order_by(User.full_name).all()
    results = []

    for u in users:
        # Calculate operator verification performance statistics
        stats = (
            db.query(
                func.count(PackingVerification.id).label("total"),
                func.coalesce(func.avg(PackingVerification.packing_score), 0.0).label("avg_score")
            )
            .filter(PackingVerification.operator_id == u.id)
            .first()
        )
        total_verifications = stats.total if stats else 0
        avg_score = round(float(stats.avg_score), 1) if stats else 0.0

        results.append(OperatorPerformanceResponse(
            id=u.id,
            full_name=u.full_name,
            email=u.email,
            role_name=u.role.name if u.role else "OPERATOR",
            store_name=u.store.store_name if u.store else None,
            is_active=u.is_active,
            is_verified=u.is_verified,
            last_login_at=u.last_login_at.isoformat() if u.last_login_at else None,
            total_verifications=total_verifications,
            avg_packing_score=avg_score
        ))

    return APIResponse(success=True, data=results)
