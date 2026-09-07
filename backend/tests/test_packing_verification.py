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
from src.security.hashing import get_password_hash
from src.security.jwt import create_access_token

client = TestClient(app)

@pytest.fixture(scope="function")
def ver_setup(db_session: Session):
    admin_role = db_session.query(Role).filter_by(name="ADMIN").first()
    token_str = uuid.uuid4().hex[:6]

    admin = User(
        full_name="Verification Tester",
        email=f"ver.tester.{token_str}@example.com",
        password_hash=get_password_hash("SecretAdmin123!"),
        role_id=admin_role.id,
        is_active=True,
        is_verified=True
    )
    db_session.add(admin)

    store = Store(store_code=f"STR-VER-{token_str.upper()}", store_name="Ver Store", location="Ver City")
    db_session.add(store)

    # 1. Fragile product
    fragile_prod = Product(sku=f"SKU-FRAG-{token_str.upper()}", name="Fragile Glass Jar", category="Preserves", weight=0.8, is_fragile=True)
    db_session.add(fragile_prod)

    # 2. Frozen product
    frozen_prod = Product(sku=f"SKU-FROZ-{token_str.upper()}", name="Frozen Ice Cream Pint", category="Frozen", weight=0.5, temperature_req="FROZEN")
    db_session.add(frozen_prod)

    # 3. Liquid product
    liquid_prod = Product(sku=f"SKU-LIQ-{token_str.upper()}", name="Fruit Juice Bottle", category="Beverages", weight=1.0, is_liquid=True)
    db_session.add(liquid_prod)

    # Packaging materials
    paper_bag = PackagingMaterial(code=f"MAT-BAG-{token_str.upper()}", name="Paper Bag", material_type="PAPER_BAG", capacity_size="MEDIUM", protection_level="LOW")
    bubble_wrap = PackagingMaterial(code=f"MAT-BUB-{token_str.upper()}", name="Bubble Wrap", material_type="BUBBLE_WRAP", capacity_size="SMALL", protection_level="HIGH")
    ice_pack = PackagingMaterial(code=f"MAT-ICE-{token_str.upper()}", name="Gel Ice Pack", material_type="ICE_PACK", capacity_size="SMALL", protection_level="MEDIUM", temperature_suitability="COLD_CHAIN")
    protective_sleeve = PackagingMaterial(code=f"MAT-SLV-{token_str.upper()}", name="Protective Sleeve", material_type="PROTECTIVE_SLEEVE", capacity_size="SMALL", protection_level="HIGH")
    db_session.add_all([paper_bag, bubble_wrap, ice_pack, protective_sleeve])

    db_session.commit()

    token = create_access_token(admin.id, role="ADMIN")
    headers = {"Authorization": f"Bearer {token}"}

    return {
        "admin": admin,
        "store": store,
        "fragile_prod": fragile_prod,
        "frozen_prod": frozen_prod,
        "liquid_prod": liquid_prod,
        "paper_bag": paper_bag,
        "bubble_wrap": bubble_wrap,
        "ice_pack": ice_pack,
        "protective_sleeve": protective_sleeve,
        "headers": headers
    }

def test_case_1_fragile_product_without_adequate_protection(ver_setup):
    """
    FAILURE CASE 1: Fragile product packed in plain paper bag without bubble wrap / sleeve.
    Expected: FAIL status or WARNING with deduction -40.
    """
    s = ver_setup
    # Create order with fragile item
    ord_res = client.post(
        f"{settings.API_V1_STR}/orders",
        json={"store_id": str(s["store"].id), "items": [{"product_id": str(s["fragile_prod"].id), "quantity": 1}]},
        headers=s["headers"]
    )
    order_id = ord_res.json()["data"]["id"]

    # Verify using paper bag only (no bubble wrap)
    ver_res = client.post(
        f"{settings.API_V1_STR}/packing-verification/verify",
        json={"order_id": order_id, "packaging_material_ids": [str(s["paper_bag"].id)], "image_path": "uploads/test.jpg"},
        headers=s["headers"]
    )
    assert ver_res.status_code == 201
    data = ver_res.json()["data"]
    assert data["status"] in ["FAIL", "WARNING"]
    assert data["packing_score"] <= 60
    assert any(v["rule_code"] == "RULE-FRAGILE-01" for v in data["violations"])

def test_case_2_frozen_product_without_cold_chain_packaging(ver_setup):
    """
    FAILURE CASE 2: Frozen product packed in plain paper bag without ice pack / cold-chain insulation.
    Expected: FAIL status with deduction -40.
    """
    s = ver_setup
    ord_res = client.post(
        f"{settings.API_V1_STR}/orders",
        json={"store_id": str(s["store"].id), "items": [{"product_id": str(s["frozen_prod"].id), "quantity": 1}]},
        headers=s["headers"]
    )
    order_id = ord_res.json()["data"]["id"]

    ver_res = client.post(
        f"{settings.API_V1_STR}/packing-verification/verify",
        json={"order_id": order_id, "packaging_material_ids": [str(s["paper_bag"].id)], "image_path": "uploads/test.jpg"},
        headers=s["headers"]
    )
    assert ver_res.status_code == 201
    data = ver_res.json()["data"]
    assert data["status"] in ["FAIL", "WARNING"]
    assert data["packing_score"] <= 60
    assert any(v["rule_code"] == "RULE-COLD-01" for v in data["violations"])

def test_case_3_liquid_and_fragile_combination_without_proper_separation(ver_setup):
    """
    FAILURE CASE 3: Liquid item + Fragile item packed together in plain bag without protective sleeve barrier.
    Expected: WARNING/FAIL status with deduction -25.
    """
    s = ver_setup
    ord_res = client.post(
        f"{settings.API_V1_STR}/orders",
        json={
            "store_id": str(s["store"].id),
            "items": [
                {"product_id": str(s["liquid_prod"].id), "quantity": 1},
                {"product_id": str(s["fragile_prod"].id), "quantity": 1}
            ]
        },
        headers=s["headers"]
    )
    order_id = ord_res.json()["data"]["id"]

    ver_res = client.post(
        f"{settings.API_V1_STR}/packing-verification/verify",
        json={"order_id": order_id, "packaging_material_ids": [str(s["paper_bag"].id)], "image_path": "uploads/test.jpg"},
        headers=s["headers"]
    )
    assert ver_res.status_code == 201
    data = ver_res.json()["data"]
    assert data["status"] in ["FAIL", "WARNING"]
    assert any(v["rule_code"] == "RULE-LIQUID-01" for v in data["violations"])

def test_successful_pass_packing_verification(ver_setup):
    """
    SUCCESS CASE: Fragile item packed with bubble wrap.
    Expected: PASS status with score >= 80.
    """
    s = ver_setup
    ord_res = client.post(
        f"{settings.API_V1_STR}/orders",
        json={"store_id": str(s["store"].id), "items": [{"product_id": str(s["fragile_prod"].id), "quantity": 1}]},
        headers=s["headers"]
    )
    order_id = ord_res.json()["data"]["id"]

    ver_res = client.post(
        f"{settings.API_V1_STR}/packing-verification/verify",
        json={"order_id": order_id, "packaging_material_ids": [str(s["bubble_wrap"].id)], "image_path": "uploads/test.jpg"},
        headers=s["headers"]
    )
    assert ver_res.status_code == 201
    data = ver_res.json()["data"]
    assert data["status"] == "PASS"
    assert data["packing_score"] >= 80
