import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.store import Store
from src.schemas.store import StoreCreate, StoreUpdate

class StoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, store_id: uuid.UUID) -> Optional[Store]:
        return self.db.query(Store).filter(Store.id == store_id).first()

    def get_by_code(self, store_code: str) -> Optional[Store]:
        return self.db.query(Store).filter(Store.store_code == store_code.strip().upper()).first()

    def get_all(self, is_active_only: bool = False, search: Optional[str] = None) -> List[Store]:
        query = self.db.query(Store)
        if is_active_only:
            query = query.filter(Store.is_active.is_(True))
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                (Store.store_name.ilike(search_term)) | (Store.store_code.ilike(search_term))
            )
        return query.order_by(Store.store_name).all()

    def create(self, store_in: StoreCreate) -> Store:
        store = Store(
            store_code=store_in.store_code.strip().upper(),
            store_name=store_in.store_name.strip(),
            location=store_in.location.strip(),
            is_active=store_in.is_active
        )
        self.db.add(store)
        self.db.commit()
        self.db.refresh(store)
        return store

    def update(self, store: Store, store_in: StoreUpdate) -> Store:
        if store_in.store_code is not None:
            store.store_code = store_in.store_code.strip().upper()
        if store_in.store_name is not None:
            store.store_name = store_in.store_name.strip()
        if store_in.location is not None:
            store.location = store_in.location.strip()
        if store_in.is_active is not None:
            store.is_active = store_in.is_active
        self.db.commit()
        self.db.refresh(store)
        return store
