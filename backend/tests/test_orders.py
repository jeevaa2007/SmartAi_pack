import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.main import app
from src.core.config import settings
from src.models.role import Role
from src.models.user import User
from src.models.store import Store
from src.models.product import Product
from src.security.hashing import get_password_hash
from src.security.jwt import create_access_token

client = TestClient(app)

@pytest.fixture(scope="function")
def admin_user_and_headers(db_session: Session):
    admin_role = db_session.query(Role).filter_by(name="ADMIN").first()
    unique_token = uuid.uuid4().hex[:6]
    admin = User(
        full_name="Admin Order Test",
        email=f"admin.order.{unique_token}@example.com",
        password_hash=get_password_hash("SecretAdmin123!"),
        role_id=admin_role.id,
        is_active=True,
        is_verified=True
    )
    db_session.add(admin)

    store = Store(
        store_code=f"STR-ORD-{unique_token.upper()}",
        store_name="Order Test Store",
        location="Test City"
    )
    db_session.add(store)

    prod = Product(
        sku=f"SKU-ORD-{unique_token.upper()}",
        name="Order Test Product",
        category="Test Category",
        weight=1.0
    )
    db_session.add(prod)
    db_session.commit()

    token = create_access_token(admin.id, role="ADMIN")
    return admin, store, prod, {"Authorization": f"Bearer {token}"}

def test_create_and_retrieve_order(admin_user_and_headers):
    admin, store, prod, headers = admin_user_and_headers

    # Create Order
    create_res = client.post(
        f"{settings.API_V1_STR}/orders",
        json={
            "store_id": str(store.id),
            "operator_id": str(admin.id),
            "items": [{"product_id": str(prod.id), "quantity": 2}]
        },
        headers=headers
    )
    assert create_res.status_code == 201
    order_data = create_res.json()["data"]
    assert order_data["verification_status"] == "UNVERIFIED"
    assert len(order_data["items"]) == 1

    # Retrieve Order
    get_res = client.get(f"{settings.API_V1_STR}/orders/{order_data['id']}", headers=headers)
    assert get_res.status_code == 200
    fetched_data = get_res.json()["data"]
    assert fetched_data["order_number"] == order_data["order_number"]
