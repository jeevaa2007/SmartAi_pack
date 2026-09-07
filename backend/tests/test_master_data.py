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
from src.models.packaging_material import PackagingMaterial
from src.models.packaging_rule import PackagingRule
from src.security.hashing import get_password_hash
from src.security.jwt import create_access_token

client = TestClient(app)

@pytest.fixture(scope="function")
def admin_headers(db_session: Session):
    admin_role = db_session.query(Role).filter_by(name="ADMIN").first()
    unique_token = uuid.uuid4().hex[:6]
    admin = User(
        full_name="Admin Test Master",
        email=f"admin.master.{unique_token}@example.com",
        password_hash=get_password_hash("SecretAdmin123!"),
        role_id=admin_role.id,
        is_active=True,
        is_verified=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    token = create_access_token(admin.id, role="ADMIN")
    return {"Authorization": f"Bearer {token}"}

def test_store_crud_and_uniqueness(admin_headers):
    unique_code = f"STR-TEST-{uuid.uuid4().hex[:4].upper()}"
    # 1. Create Store
    res = client.post(
        f"{settings.API_V1_STR}/stores",
        json={"store_code": unique_code, "store_name": "Test Dark Store", "location": "Test Loc"},
        headers=admin_headers
    )
    assert res.status_code == 201
    store_data = res.json()["data"]
    assert store_data["store_code"] == unique_code

    # 2. Duplicate Store Code Rejected
    dup_res = client.post(
        f"{settings.API_V1_STR}/stores",
        json={"store_code": unique_code, "store_name": "Duplicate Store", "location": "Test Loc"},
        headers=admin_headers
    )
    assert dup_res.status_code == 400

    # 3. List Stores
    list_res = client.get(f"{settings.API_V1_STR}/stores", headers=admin_headers)
    assert list_res.status_code == 200
    assert any(s["store_code"] == unique_code for s in list_res.json()["data"])

def test_product_crud_and_uniqueness(admin_headers):
    unique_sku = f"SKU-TEST-{uuid.uuid4().hex[:4].upper()}"
    # 1. Create Product
    res = client.post(
        f"{settings.API_V1_STR}/products",
        json={
            "sku": unique_sku,
            "name": "Fragile Glass Bottle",
            "category": "Preserves",
            "weight": 1.2,
            "is_fragile": True,
            "temperature_req": "AMBIENT",
            "is_liquid": True,
            "is_crush_sensitive": False
        },
        headers=admin_headers
    )
    assert res.status_code == 201
    prod_data = res.json()["data"]
    assert prod_data["sku"] == unique_sku
    assert prod_data["is_fragile"] is True

    # 2. Duplicate SKU Rejected
    dup_res = client.post(
        f"{settings.API_V1_STR}/products",
        json={"sku": unique_sku, "name": "Dup Product", "category": "Test", "weight": 0.5},
        headers=admin_headers
    )
    assert dup_res.status_code == 400

def test_packaging_materials_and_rules(admin_headers):
    unique_mat_code = f"MAT-TEST-{uuid.uuid4().hex[:4].upper()}"
    mat_res = client.post(
        f"{settings.API_V1_STR}/packaging/materials",
        json={
            "code": unique_mat_code,
            "name": "Test Bubble Wrap",
            "material_type": "BUBBLE_WRAP",
            "capacity_size": "SMALL",
            "protection_level": "HIGH"
        },
        headers=admin_headers
    )
    assert mat_res.status_code == 201
    assert mat_res.json()["data"]["code"] == unique_mat_code

    rule_res = client.get(f"{settings.API_V1_STR}/packaging/rules", headers=admin_headers)
    assert rule_res.status_code == 200
    assert isinstance(rule_res.json()["data"], list)
