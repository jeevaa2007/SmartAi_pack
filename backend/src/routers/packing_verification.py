import os
import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.schemas.response import APIResponse
from src.schemas.packing_verification import VerificationRequest, VerificationResponse, RuleViolationResponse
from src.repositories.order_repository import OrderRepository
from src.repositories.packaging_repository import PackagingRepository
from src.repositories.verification_repository import VerificationRepository
from src.services.rule_engine import RuleEngine
from src.api.deps import require_roles
from src.models.user import User

router = APIRouter(prefix="/packing-verification", tags=["Packing Quality Verification Engine"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024 # 5 MB

@router.post("/upload-image", response_model=APIResponse[dict])
async def upload_packing_image(
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR", "OPERATOR"]))
):
    """
    Controlled image upload endpoint for packing verification photographs.
    Validates file extension and size before storing safely on disk.
    """
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image file format '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds maximum limit of 5MB."
        )

    unique_filename = f"packing_{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(dest_path, "wb") as f:
        f.write(content)

    relative_path = f"uploads/{unique_filename}"
    return APIResponse(
        success=True,
        data={
            "filename": file.filename,
            "saved_path": relative_path,
            "content_type": file.content_type,
            "size_bytes": len(content)
        }
    )

@router.post("/verify", response_model=APIResponse[VerificationResponse], status_code=status.HTTP_201_CREATED)
def run_packing_verification(
    request: VerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR", "OPERATOR"]))
):
    """
    Runs rule-based packing quality verification engine on an order.
    Evaluates order items and sensitivity flags against selected packaging materials.
    """
    order_repo = OrderRepository(db)
    order = order_repo.get_by_id(request.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    pkg_repo = PackagingRepository(db)
    selected_materials = []
    for mat_id in request.packaging_material_ids:
        mat = pkg_repo.get_material_by_id(mat_id)
        if mat:
            selected_materials.append(mat)

    if not selected_materials:
        raise HTTPException(status_code=400, detail="At least one valid packaging material must be selected.")

    has_image = bool(request.image_path)

    # Execute deterministic Rule Engine evaluation
    packing_score, status_outcome, violations, recommendations = RuleEngine.evaluate_packing(
        order=order,
        selected_materials=selected_materials,
        has_valid_image=has_image
    )

    # Persist verification record
    ver_repo = VerificationRepository(db)
    verification = ver_repo.create_verification(
        order_id=order.id,
        operator_id=current_user.id,
        image_path=request.image_path,
        packing_score=packing_score,
        status=status_outcome,
        violations=violations,
        recommendations=recommendations
    )

    # Update order verification status and score
    order_repo.update_verification_outcome(
        order_id=order.id,
        verification_status=status_outcome,
        packing_score=packing_score,
        order_status="VERIFIED"
    )

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
        ) for v in verification.violations
    ]

    parsed_recommendations = json.loads(verification.recommendations_json) if verification.recommendations_json else []

    response_data = VerificationResponse(
        id=verification.id,
        order_id=verification.order_id,
        order_number=order.order_number,
        operator_id=verification.operator_id,
        operator_name=current_user.full_name,
        image_path=verification.image_path,
        packing_score=verification.packing_score,
        status=verification.status,
        violations=resp_violations,
        recommendations=parsed_recommendations,
        verified_at=verification.verified_at
    )

    return APIResponse(success=True, data=response_data)

@router.get("/order/{order_id}", response_model=APIResponse[Optional[VerificationResponse]])
def get_verification_by_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR", "OPERATOR"]))
):
    ver_repo = VerificationRepository(db)
    verification = ver_repo.get_by_order_id(order_id)
    if not verification:
        return APIResponse(success=True, data=None)

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
        ) for v in verification.violations
    ]

    parsed_recommendations = json.loads(verification.recommendations_json) if verification.recommendations_json else []

    response_data = VerificationResponse(
        id=verification.id,
        order_id=verification.order_id,
        order_number=verification.order.order_number if verification.order else None,
        operator_id=verification.operator_id,
        operator_name=verification.operator.full_name if verification.operator else None,
        image_path=verification.image_path,
        packing_score=verification.packing_score,
        status=verification.status,
        violations=resp_violations,
        recommendations=parsed_recommendations,
        verified_at=verification.verified_at
    )

    return APIResponse(success=True, data=response_data)
