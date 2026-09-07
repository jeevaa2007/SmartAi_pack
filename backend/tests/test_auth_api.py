import uuid
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.orm import Session

from src.core.config import settings
from src.database.connection import SessionLocal
from src.main import app
from src.models.audit_log import AuditLog
from src.models.role import Role
from src.models.user import User
from src.security.hashing import get_password_hash
from src.security.jwt import create_access_token

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    """
    Fixture providing clean PostgreSQL database session for auth API tests.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def test_admin_user(db_session: Session):
    """
    Fixture creating an active, verified ADMIN test user.
    """
    admin_role = db_session.query(Role).filter_by(name="ADMIN").first()
    unique_token = uuid.uuid4().hex[:6]
    password = "AdminTestPassword123!"
    user = User(
        full_name="Test Admin User",
        email=f"admin.test.{unique_token}@example.com",
        password_hash=get_password_hash(password),
        role_id=admin_role.id,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return {"user": user, "password": password, "email": user.email}

@pytest.fixture(scope="function")
def test_operator_user(db_session: Session):
    """
    Fixture creating an active, verified OPERATOR test user.
    """
    operator_role = db_session.query(Role).filter_by(name="OPERATOR").first()
    unique_token = uuid.uuid4().hex[:6]
    password = "OperatorTestPassword123!"
    user = User(
        full_name="Test Operator User",
        email=f"operator.test.{unique_token}@example.com",
        password_hash=get_password_hash(password),
        role_id=operator_role.id,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return {"user": user, "password": password, "email": user.email}

def test_successful_login_and_jwt_generation(test_admin_user):
    """
    1, 7, 8, 9. Test successful login returns HTTP 200, JWT token, valid claims, and user profile.
    """
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": test_admin_user["email"], "password": test_admin_user["password"]}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True

    token_data = json_data["data"]
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["expires_in"] == settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    # Validate decoded claims
    decoded = jwt.decode(
        token_data["access_token"],
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM]
    )
    assert decoded["sub"] == str(test_admin_user["user"].id)
    assert decoded["role"] == "ADMIN"
    assert "exp" in decoded and "iat" in decoded
    assert decoded["exp"] > decoded["iat"]

def test_login_incorrect_password_rejected(test_admin_user):
    """
    2. Test incorrect password returns generic 401 error.
    """
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": test_admin_user["email"], "password": "WrongPassword123!"}
    )
    assert response.status_code == 401
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"]["code"] == "AUTHENTICATION_FAILED"
    assert json_data["error"]["message"] == "Invalid email or password."

def test_login_unknown_email_rejected():
    """
    3. Test unknown email returns generic 401 error.
    """
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": f"unknown.{uuid.uuid4().hex[:6]}@example.com", "password": "SomePassword123!"}
    )
    assert response.status_code == 401
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"]["code"] == "AUTHENTICATION_FAILED"
    assert json_data["error"]["message"] == "Invalid email or password."

def test_login_email_normalization(test_admin_user):
    """
    4. Test login accepts unnormalized email (spaces, uppercase) and authenticates successfully.
    """
    unnormalized = f"  {test_admin_user['email'].upper()}  "
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": unnormalized, "password": test_admin_user["password"]}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_inactive_user_login_rejected(db_session: Session):
    """
    5. Test inactive user (is_active=False) login is rejected with generic 401 error.
    """
    admin_role = db_session.query(Role).filter_by(name="ADMIN").first()
    password = "Password123!"
    user = User(
        full_name="Inactive User",
        email=f"inactive.{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash(password),
        role_id=admin_role.id,
        is_active=False,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": user.email, "password": password}
    )
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid email or password."

def test_unverified_user_login_rejected(db_session: Session):
    """
    6. Test unverified user (is_verified=False) login is rejected with generic 401 error.
    """
    admin_role = db_session.query(Role).filter_by(name="ADMIN").first()
    password = "Password123!"
    user = User(
        full_name="Unverified User",
        email=f"unverified.{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash(password),
        role_id=admin_role.id,
        is_active=True,
        is_verified=False
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": user.email, "password": password}
    )
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid email or password."

def test_get_current_user_me_success(test_admin_user):
    """
    10, 16, 17. Test GET /api/v1/auth/me returns current authenticated user profile without password_hash.
    """
    login_res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": test_admin_user["email"], "password": test_admin_user["password"]}
    )
    token = login_res.json()["data"]["access_token"]

    me_res = client.get(
        f"{settings.API_V1_STR}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    user_data = me_res.json()["data"]

    assert user_data["id"] == str(test_admin_user["user"].id)
    assert user_data["email"] == test_admin_user["email"]
    assert user_data["role"] == "ADMIN"
    assert "password_hash" not in user_data
    assert "password" not in user_data

def test_get_me_missing_token_rejected():
    """
    11. Test GET /auth/me without Authorization header returns 401 Unauthorized.
    """
    response = client.get(f"{settings.API_V1_STR}/auth/me")
    assert response.status_code == 401

def test_get_me_malformed_token_rejected():
    """
    12. Test GET /auth/me with malformed Bearer token returns 401 Unauthorized.
    """
    response = client.get(
        f"{settings.API_V1_STR}/auth/me",
        headers={"Authorization": "Bearer invalid.malformed.token"}
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"

def test_get_me_expired_token_rejected(test_admin_user):
    """
    13. Test GET /auth/me with expired JWT token returns 401 Unauthorized.
    """
    expired_token = create_access_token(
        subject=test_admin_user["user"].id,
        role="ADMIN",
        expires_delta=timedelta(seconds=-10)
    )
    response = client.get(
        f"{settings.API_V1_STR}/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"

def test_get_me_invalid_signature_rejected(test_admin_user):
    """
    14. Test GET /auth/me with token signed by invalid secret returns 401 Unauthorized.
    """
    bad_token = jwt.encode(
        {"sub": str(test_admin_user["user"].id), "role": "ADMIN"},
        "wrong-secret-key-12345678901234567890",
        algorithm=settings.JWT_ALGORITHM
    )
    response = client.get(
        f"{settings.API_V1_STR}/auth/me",
        headers={"Authorization": f"Bearer {bad_token}"}
    )
    assert response.status_code == 401

def test_get_me_nonexistent_user_token_rejected():
    """
    15. Test token referencing nonexistent user UUID is rejected with 401 Unauthorized.
    """
    nonexistent_id = uuid.uuid4()
    token = create_access_token(subject=nonexistent_id, role="ADMIN")
    response = client.get(
        f"{settings.API_V1_STR}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401

def test_role_authorization_dependency(test_admin_user, test_operator_user):
    """
    18, 19, 20, 21. Test RBAC require_roles dependency permits matching roles and rejects unauthorized roles with 403.
    """
    from src.api.deps import require_roles

    admin_checker = require_roles("ADMIN")
    operator_checker = require_roles("OPERATOR")

    # Admin user passes admin checker
    assert admin_checker(current_user=test_admin_user["user"]).id == test_admin_user["user"].id

    # Operator user fails admin checker with AuthorizationError (403)
    from src.core.exceptions import AuthorizationError
    with pytest.raises(AuthorizationError) as exc_info:
        admin_checker(current_user=test_operator_user["user"])
    assert exc_info.value.status_code == 403
    assert exc_info.value.code == "PERMISSION_DENIED"

    # Operator user passes operator checker
    assert operator_checker(current_user=test_operator_user["user"]).id == test_operator_user["user"].id

def test_last_login_at_updated_on_successful_login(db_session: Session, test_admin_user):
    """
    22, 23. Test successful login updates last_login_at timestamp, while failed login does not.
    """
    initial_last_login = test_admin_user["user"].last_login_at

    # Failed login
    client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": test_admin_user["email"], "password": "WrongPassword!"}
    )
    db_session.refresh(test_admin_user["user"])
    assert test_admin_user["user"].last_login_at == initial_last_login

    # Successful login
    client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": test_admin_user["email"], "password": test_admin_user["password"]}
    )
    db_session.refresh(test_admin_user["user"])
    assert test_admin_user["user"].last_login_at is not None
    assert test_admin_user["user"].last_login_at.tzinfo is not None

def test_audit_logs_created_on_login(db_session: Session, test_admin_user):
    """
    24, 25. Test LOGIN_SUCCESS and LOGIN_FAILED audit log entries are persisted to audit_logs table.
    """
    req_id = f"req-test-audit-failed-{uuid.uuid4().hex[:6]}"

    # 1. Trigger LOGIN_FAILED
    client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": test_admin_user["email"], "password": "WrongPassword!"},
        headers={"X-Request-ID": req_id}
    )
    failed_log = (
        db_session.query(AuditLog)
        .filter(AuditLog.request_id == req_id, AuditLog.action == "LOGIN_FAILED")
        .first()
    )
    assert failed_log is not None
    assert failed_log.user_id == test_admin_user["user"].id

    # 2. Trigger LOGIN_SUCCESS
    success_req_id = f"req-test-audit-success-{uuid.uuid4().hex[:6]}"
    client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": test_admin_user["email"], "password": test_admin_user["password"]},
        headers={"X-Request-ID": success_req_id}
    )
    success_log = (
        db_session.query(AuditLog)
        .filter(AuditLog.request_id == success_req_id, AuditLog.action == "LOGIN_SUCCESS")
        .first()
    )
    assert success_log is not None
    assert success_log.user_id == test_admin_user["user"].id

def test_middleware_security_headers_and_correlation(test_admin_user):
    """
    26, 27. Test existing security headers, correlation ID headers, and rate limiting headers remain active.
    """
    req_id = f"correlation-test-{uuid.uuid4().hex[:6]}"
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": test_admin_user["email"], "password": test_admin_user["password"]},
        headers={"X-Request-ID": req_id}
    )
    assert response.status_code == 200
    headers = response.headers

    # Security Headers
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-Content-Type-Options") == "nosniff"

    # Correlation ID Header
    assert headers.get("X-Request-ID") == req_id

    # Rate Limit Header
    assert "X-RateLimit-Limit" in headers
