import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.schemas.response import APIResponse
from src.schemas.packaging import (
    PackagingMaterialCreate,
    PackagingMaterialResponse,
    PackagingRuleCreate,
    PackagingRuleResponse
)
from src.repositories.packaging_repository import PackagingRepository
from src.api.deps import require_roles
from src.models.user import User

router = APIRouter(prefix="/packaging", tags=["Packaging Materials & Quality Rules"])

# Materials
@router.get("/materials", response_model=APIResponse[List[PackagingMaterialResponse]])
def list_materials(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR", "OPERATOR"]))
):
    repo = PackagingRepository(db)
    mats = repo.get_all_materials(is_active_only=True)
    return APIResponse(success=True, data=mats)

@router.post("/materials", response_model=APIResponse[PackagingMaterialResponse], status_code=status.HTTP_201_CREATED)
def create_material(
    mat_in: PackagingMaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR"]))
):
    repo = PackagingRepository(db)
    if repo.get_material_by_code(mat_in.code):
        raise HTTPException(status_code=400, detail=f"Packaging material code '{mat_in.code}' already exists.")
    mat = repo.create_material(mat_in)
    return APIResponse(success=True, data=mat)

# Rules
@router.get("/rules", response_model=APIResponse[List[PackagingRuleResponse]])
def list_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR", "OPERATOR"]))
):
    repo = PackagingRepository(db)
    rules = repo.get_all_rules(is_active_only=True)
    return APIResponse(success=True, data=rules)

@router.post("/rules", response_model=APIResponse[PackagingRuleResponse], status_code=status.HTTP_201_CREATED)
def create_rule(
    rule_in: PackagingRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR"]))
):
    repo = PackagingRepository(db)
    rule = repo.create_rule(rule_in)
    return APIResponse(success=True, data=rule)
