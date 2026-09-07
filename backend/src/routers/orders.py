import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.schemas.response import APIResponse
from src.schemas.order import OrderCreate, OrderResponse
from src.repositories.order_repository import OrderRepository
from src.api.deps import require_roles
from src.models.user import User

router = APIRouter(prefix="/orders", tags=["Order Management"])

def _to_order_response(order) -> OrderResponse:
    items = []
    if order.items:
        for item in order.items:
            items.append({
                "id": item.id,
                "order_id": item.order_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "item_attributes_snapshot": item.item_attributes_snapshot,
                "product": item.product
            })

    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        store_id=order.store_id,
        store_code=order.store.store_code if order.store else None,
        store_name=order.store.store_name if order.store else None,
        operator_id=order.operator_id,
        operator_name=order.operator.full_name if order.operator else None,
        status=order.status,
        verification_status=order.verification_status,
        packing_score=order.packing_score,
        items=items,
        created_at=order.created_at,
        updated_at=order.updated_at
    )

@router.get("", response_model=APIResponse[List[OrderResponse]])
def list_orders(
    store_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    verification_status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(200, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR", "OPERATOR"]))
):
    repo = OrderRepository(db)
    orders = repo.get_all(
        store_id=store_id,
        status=status,
        verification_status=verification_status,
        search=search,
        limit=limit
    )
    result = [_to_order_response(o) for o in orders]
    return APIResponse(success=True, data=result)

@router.get("/{order_id}", response_model=APIResponse[OrderResponse])
def get_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR", "OPERATOR"]))
):
    repo = OrderRepository(db)
    order = repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return APIResponse(success=True, data=_to_order_response(order))

@router.post("", response_model=APIResponse[OrderResponse], status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR", "OPERATOR"]))
):
    repo = OrderRepository(db)
    # Generate unique order number: ORD-YYYYMMDD-XXXX
    unique_suffix = uuid.uuid4().hex[:6].upper()
    order_number = f"ORD-{unique_suffix}"

    # Default operator_id to current_user if not specified
    if not order_in.operator_id:
        order_in.operator_id = current_user.id

    try:
        order = repo.create_order(order_number, order_in)
        return APIResponse(success=True, data=_to_order_response(order))
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
