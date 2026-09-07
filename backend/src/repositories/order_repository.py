import uuid
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from src.models.order import Order, OrderItem
from src.models.product import Product
from src.models.store import Store
from src.schemas.order import OrderCreate

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(
                joinedload(Order.store),
                joinedload(Order.operator),
                joinedload(Order.items).joinedload(OrderItem.product)
            )
            .filter(Order.id == order_id)
            .first()
        )

    def get_by_number(self, order_number: str) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(
                joinedload(Order.store),
                joinedload(Order.operator),
                joinedload(Order.items).joinedload(OrderItem.product)
            )
            .filter(Order.order_number == order_number.strip().upper())
            .first()
        )

    def get_all(
        self,
        store_id: Optional[uuid.UUID] = None,
        operator_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        verification_status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 200
    ) -> List[Order]:
        query = self.db.query(Order).options(
            joinedload(Order.store),
            joinedload(Order.operator),
            joinedload(Order.items).joinedload(OrderItem.product)
        )
        if store_id:
            query = query.filter(Order.store_id == store_id)
        if operator_id:
            query = query.filter(Order.operator_id == operator_id)
        if status:
            query = query.filter(Order.status == status)
        if verification_status:
            query = query.filter(Order.verification_status == verification_status)
        if search:
            term = f"%{search.strip()}%"
            query = query.filter(Order.order_number.ilike(term))
        return query.order_by(Order.created_at.desc()).limit(limit).all()

    def create_order(self, order_number: str, order_in: OrderCreate) -> Order:
        order = Order(
            order_number=order_number,
            store_id=order_in.store_id,
            operator_id=order_in.operator_id,
            status="CREATED",
            verification_status="UNVERIFIED"
        )
        self.db.add(order)
        self.db.flush()

        for item_in in order_in.items:
            product = self.db.query(Product).filter(Product.id == item_in.product_id).first()
            if not product:
                raise ValueError(f"Product ID {item_in.product_id} not found.")

            snapshot = {
                "sku": product.sku,
                "name": product.name,
                "is_fragile": product.is_fragile,
                "temperature_req": product.temperature_req,
                "is_liquid": product.is_liquid,
                "is_crush_sensitive": product.is_crush_sensitive,
                "category": product.category,
                "weight": product.weight
            }
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item_in.quantity,
                item_attributes_snapshot=str(snapshot)
            )
            self.db.add(order_item)

        self.db.commit()
        return self.get_by_id(order.id)

    def update_verification_outcome(
        self,
        order_id: uuid.UUID,
        verification_status: str,
        packing_score: int,
        order_status: str = "VERIFIED"
    ) -> Order:
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.verification_status = verification_status
            order.packing_score = packing_score
            order.status = order_status
            self.db.commit()
            self.db.refresh(order)
        return order
