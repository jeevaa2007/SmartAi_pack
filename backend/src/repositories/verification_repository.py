import uuid
import json
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from src.models.packing_verification import PackingVerification, RuleViolation
from src.schemas.packing_verification import RuleViolationResponse

class VerificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, verification_id: uuid.UUID) -> Optional[PackingVerification]:
        return (
            self.db.query(PackingVerification)
            .options(
                joinedload(PackingVerification.order),
                joinedload(PackingVerification.operator),
                joinedload(PackingVerification.violations)
            )
            .filter(PackingVerification.id == verification_id)
            .first()
        )

    def get_by_order_id(self, order_id: uuid.UUID) -> Optional[PackingVerification]:
        return (
            self.db.query(PackingVerification)
            .options(
                joinedload(PackingVerification.order),
                joinedload(PackingVerification.operator),
                joinedload(PackingVerification.violations)
            )
            .filter(PackingVerification.order_id == order_id)
            .order_by(PackingVerification.verified_at.desc())
            .first()
        )

    def get_recent(self, limit: int = 20) -> List[PackingVerification]:
        return (
            self.db.query(PackingVerification)
            .options(
                joinedload(PackingVerification.order),
                joinedload(PackingVerification.operator),
                joinedload(PackingVerification.violations)
            )
            .order_by(PackingVerification.verified_at.desc())
            .limit(limit)
            .all()
        )

    def create_verification(
        self,
        order_id: uuid.UUID,
        operator_id: Optional[uuid.UUID],
        image_path: Optional[str],
        packing_score: int,
        status: str,
        violations: List[RuleViolationResponse],
        recommendations: List[str]
    ) -> PackingVerification:
        violations_dicts = [v.model_dump() for v in violations]

        pv = PackingVerification(
            order_id=order_id,
            operator_id=operator_id,
            image_path=image_path,
            packing_score=packing_score,
            status=status,
            violations_json=json.dumps(violations_dicts),
            recommendations_json=json.dumps(recommendations)
        )
        self.db.add(pv)
        self.db.flush()

        for v_dto in violations:
            rv = RuleViolation(
                verification_id=pv.id,
                rule_code=v_dto.rule_code,
                rule_name=v_dto.rule_name,
                severity=v_dto.severity,
                description=v_dto.description,
                detected_value=v_dto.detected_value,
                expected_value=v_dto.expected_value,
                deduction=v_dto.deduction
            )
            self.db.add(rv)

        self.db.commit()
        return self.get_by_id(pv.id)
