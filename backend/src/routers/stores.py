import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.schemas.response import APIResponse
from src.schemas.store import StoreCreate, StoreUpdate, StoreResponse
from src.repositories.store_repository import StoreRepository
from src.api.deps import get_current_user, require_roles
from src.models.user import User

router = APIRouter(prefix="/stores", tags=["Store Master Data"])

@router.get("", response_model=APIResponse[List[StoreResponse]])
def list_stores(
    search: Optional[str] = None,
    is_active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR", "OPERATOR"]))
):
    repo = StoreRepository(db)
    stores = repo.get_all(is_active_only=is_active_only, search=search)
    return APIResponse(success=True, data=stores)

@router.get("/{store_id}", response_model=APIResponse[StoreResponse])
def get_store(
    store_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR", "OPERATOR"]))
):
    repo = StoreRepository(db)
    store = repo.get_by_id(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return APIResponse(success=True, data=store)

@router.post("", response_model=APIResponse[StoreResponse], status_code=status.HTTP_201_CREATED)
def create_store(
    store_in: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR"]))
):
    repo = StoreRepository(db)
    if repo.get_by_code(store_in.store_code):
        raise HTTPException(status_code=400, detail=f"Store code '{store_in.store_code}' already exists.")
    store = repo.create(store_in)
    return APIResponse(success=True, data=store)

@router.put("/{store_id}", response_model=APIResponse[StoreResponse])
def update_store(
    store_id: uuid.UUID,
    store_in: StoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "SUPERVISOR"]))
):
    repo = StoreRepository(db)
    store = repo.get_by_id(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    if store_in.store_code and store_in.store_code != store.store_code:
        if repo.get_by_code(store_in.store_code):
            raise HTTPException(status_code=400, detail=f"Store code '{store_in.store_code}' already exists.")
    updated_store = repo.update(store, store_in)
    return APIResponse(success=True, data=updated_store)
