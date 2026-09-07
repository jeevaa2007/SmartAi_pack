import uuid
from typing import Optional
from sqlalchemy.orm import Session
from loguru import logger
from src.core.config import settings
from src.core.exceptions import AuthenticationError
from src.repositories.user_repository import UserRepository
from src.repositories.audit_repository import AuditRepository
from src.schemas.auth import AuthenticatedUserResponse, TokenData
from src.security.hashing import verify_password
from src.security.jwt import create_access_token

class AuthService:
    """
    Domain service handling user authentication, credential validation, audit event logging,
    and JWT access token issuance.
    """

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> TokenData:
        """
        Authenticates incoming user credentials, enforces account active/verified states,
        updates last_login_at, creates audit log trails, and returns a signed JWT TokenData payload.
        """
        if not email or not password:
            raise AuthenticationError("Invalid email or password.")

        normalized_email = email.strip().lower()
        user = UserRepository.get_by_email(db, normalized_email)

        # Handle unknown email
        if not user:
            logger.warning(f"Login failed: Unknown email address '{normalized_email}' from IP: {ip_address}")
            AuditRepository.create_audit_entry(
                db=db,
                user_id=None,
                action="LOGIN_FAILED",
                description=f"Authentication failed for email: {normalized_email}",
                ip_address=ip_address,
                request_id=request_id
            )
            raise AuthenticationError("Invalid email or password.")

        # Verify password hash
        if not verify_password(password, user.password_hash):
            logger.warning(f"Login failed: Incorrect password for user_id={user.id} from IP: {ip_address}")
            AuditRepository.create_audit_entry(
                db=db,
                user_id=user.id,
                action="LOGIN_FAILED",
                resource_type="USER",
                resource_id=user.id,
                description="Authentication failed: incorrect password",
                ip_address=ip_address,
                request_id=request_id
            )
            raise AuthenticationError("Invalid email or password.")

        # Check account status (is_active & is_verified)
        if not user.is_active or not user.is_verified:
            logger.warning(f"Login failed: Inactive or unverified account status (active={user.is_active}, verified={user.is_verified}) for user_id={user.id}")
            AuditRepository.create_audit_entry(
                db=db,
                user_id=user.id,
                action="LOGIN_FAILED",
                resource_type="USER",
                resource_id=user.id,
                description=f"Authentication failed: is_active={user.is_active}, is_verified={user.is_verified}",
                ip_address=ip_address,
                request_id=request_id
            )
            raise AuthenticationError("Invalid email or password.")

        # Authentication Successful
        UserRepository.update_last_login(db, user.id)
        AuditRepository.create_audit_entry(
            db=db,
            user_id=user.id,
            action="LOGIN_SUCCESS",
            resource_type="USER",
            resource_id=user.id,
            description="User logged in successfully",
            ip_address=ip_address,
            request_id=request_id
        )

        role_name = user.role.name if user.role else "OPERATOR"
        access_token = create_access_token(subject=user.id, role=role_name)
        expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        user_profile = AuthenticatedUserResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            role=role_name,
            store_id=user.store_id,
            is_active=user.is_active,
            is_verified=user.is_verified
        )

        logger.info(f"User authenticated successfully: user_id={user.id}, role={role_name}")
        return TokenData(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in_seconds,
            user=user_profile
        )
