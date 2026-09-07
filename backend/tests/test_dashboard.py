import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.main import app
from src.core.config import settings
from src.models.role import Role
from src.models.user import User
from src.security.hashing import get_password_hash
from src.security.jwt import create_access_token
import uuid

client = TestClient(app)

@pytest.fixture(scope="function")
def admin_headers(db_session: Session):
    admin_role = db_session.query(Role).filter_by(name="ADMIN").first()
    unique_token = uuid.uuid4().hex[:6]
    admin = User(
        full_name="Dashboard Test Admin",
        email=f"dash.admin.{unique_token}@example.com",
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

def test_get_dashboard_stats(admin_headers):
    res = client.get(f"{settings.API_V1_STR}/dashboard/stats", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "total_orders" in data["data"]
    assert "verified_orders" in data["data"]
    assert "pass_rate" in data["data"]
    assert "outcome_breakdown" in data["data"]

def test_get_dashboard_stats_with_store_id(admin_headers):
    random_store_id = str(uuid.uuid4())
    res = client.get(f"{settings.API_V1_STR}/dashboard/stats?store_id={random_store_id}", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "total_orders" in data["data"]
