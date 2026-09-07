import json
import uuid
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.database.connection import get_db
from src.schemas.response import APIResponse
from src.schemas.dashboard import DashboardStatsResponse, OutcomeBreakdown
from src.repositories.order_repository import OrderRepository
from src.repositories.verification_repository import VerificationRepository
from src.models.order import Order
from src.models.packing_verification import PackingVerification
from src.schemas.packing_verification import VerificationResponse, RuleViolationResponse
from src.api.deps import require_roles
from src.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Operational Control Center Dashboard"])

@router.get("/stats", response_model=APIResponse[DashboardStatsResponse])
def get_dashboard_stats(
    store_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR", "OPERATOR"]))
):
    """
    Computes real-time dark store KPI analytics and verification activity metrics.
    """
    order_query = db.query(Order)
    ver_query = db.query(PackingVerification)

    if store_id:
        try:
            sid = uuid.UUID(store_id)
            order_query = order_query.filter(Order.store_id == sid)
            ver_query = ver_query.join(Order).filter(Order.store_id == sid)
        except Exception:
            pass

    total_orders = order_query.count()
    verified_orders = order_query.filter(Order.verification_status != "UNVERIFIED").count()

    pass_count = ver_query.filter(PackingVerification.status == "PASS").count()
    warning_count = ver_query.filter(PackingVerification.status == "WARNING").count()
    fail_count = ver_query.filter(PackingVerification.status == "FAIL").count()

    total_verifications = pass_count + warning_count + fail_count
    pass_rate = round((pass_count / total_verifications * 100.0), 1) if total_verifications > 0 else 0.0

    avg_score_res = db.query(func.coalesce(func.avg(PackingVerification.packing_score), 0.0)).scalar()
    avg_packing_score = round(float(avg_score_res), 1)

    order_repo = OrderRepository(db)
    recent_orders_raw = order_repo.get_all(limit=5)
    recent_orders = [
        {
            "id": o.id,
            "order_number": o.order_number,
            "store_id": o.store_id,
            "store_code": o.store.store_code if o.store else None,
            "store_name": o.store.store_name if o.store else None,
            "operator_id": o.operator_id,
            "operator_name": o.operator.full_name if o.operator else None,
            "status": o.status,
            "verification_status": o.verification_status,
            "packing_score": o.packing_score,
            "items": [],
            "created_at": o.created_at,
            "updated_at": o.updated_at
        } for o in recent_orders_raw
    ]

    ver_repo = VerificationRepository(db)
    recent_vers_raw = ver_repo.get_recent(limit=5)
    recent_verifications = []

    for pv in recent_vers_raw:
        resp_violations = [
            RuleViolationResponse(
                id=v.id,
                rule_code=v.rule_code,
                rule_name=v.rule_name,
                severity=v.severity,
                description=v.description,
                detected_value=v.detected_value,
                expected_value=v.expected_value,
                deduction=v.deduction
            ) for v in pv.violations
        ]
        parsed_recs = json.loads(pv.recommendations_json) if pv.recommendations_json else []

        recent_verifications.append(VerificationResponse(
            id=pv.id,
            order_id=pv.order_id,
            order_number=pv.order.order_number if pv.order else None,
            operator_id=pv.operator_id,
            operator_name=pv.operator.full_name if pv.operator else None,
            image_path=pv.image_path,
            packing_score=pv.packing_score,
            status=pv.status,
            violations=resp_violations,
            recommendations=parsed_recs,
            verified_at=pv.verified_at
        ))

    data = DashboardStatsResponse(
        total_orders=total_orders,
        verified_orders=verified_orders,
        pass_rate=pass_rate,
        warning_count=warning_count,
        failure_count=fail_count,
        avg_packing_score=avg_packing_score,
        recent_orders=recent_orders,
        recent_verifications=recent_verifications,
        outcome_breakdown=OutcomeBreakdown(
            pass_count=pass_count,
            warning_count=warning_count,
            fail_count=fail_count
        )
    )

    return APIResponse(success=True, data=data)
