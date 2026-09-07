import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from src.database.connection import SessionLocal, engine
from src.models.role import Role
from src.models.user import User
from src.models.audit_log import AuditLog
from src.security.hashing import get_password_hash, verify_password

@pytest.fixture(scope="function")
def db_session():
    """
    Fixture providing a clean database session for test isolation.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

def test_initial_roles_seeded(db_session):
    """
    1. Verify required initial roles (ADMIN, SUPERVISOR, OPERATOR) exist in database.
    """
    admin_role = db_session.query(Role).filter_by(name="ADMIN").first()
    supervisor_role = db_session.query(Role).filter_by(name="SUPERVISOR").first()
    operator_role = db_session.query(Role).filter_by(name="OPERATOR").first()

    assert admin_role is not None, "ADMIN role should exist"
    assert supervisor_role is not None, "SUPERVISOR role should exist"
    assert operator_role is not None, "OPERATOR role should exist"
    assert admin_role.is_active is True
    assert isinstance(admin_role.id, uuid.UUID)

def test_role_creation_and_fields(db_session):
    """
    2. Test custom role creation, UUID generation, and timestamp assignment.
    """
    role = Role(
        name=f"CUSTOM_ROLE_{uuid.uuid4().hex[:8]}",
        description="Temporary test role"
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)

    assert isinstance(role.id, uuid.UUID)
    assert role.is_active is True
    assert role.created_at.tzinfo is not None, "Timestamp must be timezone-aware"

def test_duplicate_role_name_rejected(db_session):
    """
    3. Test unique constraint enforcement on role name.
    """
    role_name = f"UNIQUE_ROLE_{uuid.uuid4().hex[:8]}"
    role1 = Role(name=role_name, description="First role")
    db_session.add(role1)
    db_session.commit()

    role2 = Role(name=role_name, description="Duplicate role")
    db_session.add(role2)
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_user_creation_and_password_hash(db_session):
    """
    4. Test User creation with password_hash using Phase 2 security utility.
    """
    admin_role = db_session.query(Role).filter_by(name="ADMIN").first()
    raw_password = "SecurePassword123!"
    hashed_pwd = get_password_hash(raw_password)

    user = User(
        full_name="John Doe",
        email=f"john.doe_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=hashed_pwd,
        role_id=admin_role.id,
        store_id=None
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert isinstance(user.id, uuid.UUID)
    assert user.email.startswith("john.doe_")
    assert user.password_hash != raw_password
    assert verify_password(raw_password, user.password_hash) is True
    assert user.store_id is None, "store_id must be nullable without FK constraint"
    assert user.created_at.tzinfo is not None

def test_email_normalization_whitespace_and_lowercase(db_session):
    """
    5. Test email normalization trims surrounding whitespace and lowercases input.
    """
    admin_role = db_session.query(Role).filter_by(name="ADMIN").first()
    unique_token = uuid.uuid4().hex[:6]
    unnormalized_email = f"  Test.User.{unique_token}@Domain.COM  "
    expected_email = f"test.user.{unique_token}@domain.com"

    user = User(
        full_name="Jane Normalizer",
        email=unnormalized_email,
        password_hash=get_password_hash("SecretPass123"),
        role_id=admin_role.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.email == expected_email, "Email must be normalized (trimmed + lowercased)"

def test_duplicate_user_email_rejected_normalized(db_session):
    """
    6. Test uniqueness constraint prevents duplicate normalized email addresses.
    """
    admin_role = db_session.query(Role).filter_by(name="ADMIN").first()
    unique_token = uuid.uuid4().hex[:6]
    base_email = f"unique.{unique_token}@example.com"

    user1 = User(
        full_name="User One",
        email=base_email,
        password_hash=get_password_hash("Secret123"),
        role_id=admin_role.id
    )
    db_session.add(user1)
    db_session.commit()

    # Attempt to insert uppercase variant
    user2 = User(
        full_name="User Two",
        email=f" UNIQUE.{unique_token}@EXAMPLE.COM ",
        password_hash=get_password_hash("Secret123"),
        role_id=admin_role.id
    )
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_user_role_relationships(db_session):
    """
    7. Test bidirectional navigation between User and Role models.
    """
    supervisor_role = db_session.query(Role).filter_by(name="SUPERVISOR").first()
    user = User(
        full_name="Supervisor User",
        email=f"sup_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Pass123"),
        role_id=supervisor_role.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Test N -> 1 User.role navigation
    assert user.role.name == "SUPERVISOR"

    # Test 1 -> N Role.users navigation
    role_user_ids = [u.id for u in supervisor_role.users]
    assert user.id in role_user_ids

def test_audit_log_user_relationship(db_session):
    """
    8. Test AuditLog creation and bidirectional relationship with User.
    """
    operator_role = db_session.query(Role).filter_by(name="OPERATOR").first()
    user = User(
        full_name="Operator User",
        email=f"op_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Pass123"),
        role_id=operator_role.id
    )
    db_session.add(user)
    db_session.commit()

    audit_entry = AuditLog(
        user_id=user.id,
        action="USER_CREATED",
        resource_type="USER",
        resource_id=user.id,
        description="User account created for testing",
        ip_address="127.0.0.1",
        request_id="req-test-123"
    )
    db_session.add(audit_entry)
    db_session.commit()
    db_session.refresh(audit_entry)

    assert isinstance(audit_entry.id, uuid.UUID)
    assert audit_entry.user.id == user.id
    assert audit_entry.created_at.tzinfo is not None

def test_deleting_role_assigned_to_user_prevented(db_session):
    """
    9. Test FK constraint prevents deleting a Role assigned to active users (RESTRICT behavior).
    """
    temp_role = Role(
        name=f"TEMP_RESTRICT_ROLE_{uuid.uuid4().hex[:6]}",
        description="Role for testing deletion restriction"
    )
    db_session.add(temp_role)
    db_session.commit()

    user = User(
        full_name="Assigned User",
        email=f"assigned_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Pass123"),
        role_id=temp_role.id
    )
    db_session.add(user)
    db_session.commit()

    # Attempt to delete the role directly
    db_session.delete(temp_role)
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_deleting_user_sets_audit_log_user_id_null(db_session):
    """
    10. Test deleting a User sets audit_logs.user_id to NULL while preserving the audit record.
    """
    operator_role = db_session.query(Role).filter_by(name="OPERATOR").first()
    user = User(
        full_name="Transient User",
        email=f"transient_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Pass123"),
        role_id=operator_role.id
    )
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    audit_entry = AuditLog(
        user_id=user_id,
        action="LOGIN",
        description="Transient user login audit event",
        ip_address="192.168.1.1"
    )
    db_session.add(audit_entry)
    db_session.commit()
    audit_id = audit_entry.id

    # Delete the user record
    db_session.delete(user)
    db_session.commit()

    # Fetch audit log entry to verify user_id is set to NULL while entry persists
    audit_after = db_session.query(AuditLog).filter_by(id=audit_id).first()
    assert audit_after is not None, "Audit log record must be preserved"
    assert audit_after.user_id is None, "audit_logs.user_id must be set to NULL on user deletion"
