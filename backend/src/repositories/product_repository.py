import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.product import Product
from src.schemas.product import ProductCreate, ProductUpdate

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: uuid.UUID) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_sku(self, sku: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.sku == sku.strip().upper()).first()

    def get_all(
        self,
        is_active_only: bool = False,
        category: Optional[str] = None,
        is_fragile: Optional[bool] = None,
        temperature_req: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 500
    ) -> List[Product]:
        query = self.db.query(Product)
        if is_active_only:
            query = query.filter(Product.is_active.is_(True))
        if category:
            query = query.filter(Product.category == category)
        if is_fragile is not None:
            query = query.filter(Product.is_fragile.is_(is_fragile))
        if temperature_req:
            query = query.filter(Product.temperature_req == temperature_req)
        if search:
            term = f"%{search.strip()}%"
            query = query.filter((Product.name.ilike(term)) | (Product.sku.ilike(term)))
        return query.order_by(Product.name).limit(limit).all()

    def create(self, product_in: ProductCreate) -> Product:
        product = Product(
            sku=product_in.sku.strip().upper(),
            name=product_in.name.strip(),
            category=product_in.category.strip(),
            weight=product_in.weight,
            dimensions=product_in.dimensions,
            is_fragile=product_in.is_fragile,
            temperature_req=product_in.temperature_req,
            is_liquid=product_in.is_liquid,
            is_crush_sensitive=product_in.is_crush_sensitive,
            preferred_packaging_type=product_in.preferred_packaging_type,
            is_active=product_in.is_active
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product: Product, product_in: ProductUpdate) -> Product:
        for field, value in product_in.model_dump(exclude_unset=True).items():
            if field == "sku" and value:
                setattr(product, field, value.strip().upper())
            elif isinstance(value, str):
                setattr(product, field, value.strip())
            elif value is not None:
                setattr(product, field, value)
        self.db.commit()
        self.db.refresh(product)
        return product
