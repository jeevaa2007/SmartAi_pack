import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.schemas.response import APIResponse
from src.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from src.repositories.product_repository import ProductRepository
from src.api.deps import require_roles
from src.models.user import User

router = APIRouter(prefix="/products", tags=["Product Catalog"])

@router.get("", response_model=APIResponse[List[ProductResponse]])
def list_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_fragile: Optional[bool] = None,
    temperature_req: Optional[str] = None,
    is_active_only: bool = False,
    limit: int = Query(500, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR", "OPERATOR"]))
):
    repo = ProductRepository(db)
    products = repo.get_all(
        is_active_only=is_active_only,
        category=category,
        is_fragile=is_fragile,
        temperature_req=temperature_req,
        search=search,
        limit=limit
    )
    return APIResponse(success=True, data=products)

@router.get("/{product_id}", response_model=APIResponse[ProductResponse])
def get_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR", "OPERATOR"]))
):
    repo = ProductRepository(db)
    product = repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return APIResponse(success=True, data=product)

@router.post("", response_model=APIResponse[ProductResponse], status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR"]))
):
    repo = ProductRepository(db)
    if repo.get_by_sku(product_in.sku):
        raise HTTPException(status_code=400, detail=f"Product SKU '{product_in.sku}' already exists.")
    product = repo.create(product_in)
    return APIResponse(success=True, data=product)

@router.put("/{product_id}", response_model=APIResponse[ProductResponse])
def update_product(
    product_id: uuid.UUID,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR"]))
):
    repo = ProductRepository(db)
    product = repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product_in.sku and product_in.sku != product.sku:
        if repo.get_by_sku(product_in.sku):
            raise HTTPException(status_code=400, detail=f"Product SKU '{product_in.sku}' already exists.")
    updated = repo.update(product, product_in)
    return APIResponse(success=True, data=updated)
