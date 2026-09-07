import uuid
from typing import Callable, List, Optional
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from loguru import logger

from src.core.config import settings
from src.core.exceptions import AuthenticationError, AuthorizationError
from src.database.connection import get_db
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.security.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    FastAPI dependency extracting and validating the incoming Bearer JWT access token.
    Decodes subject payload, loads current active user from PostgreSQL, and returns User ORM model.
    """
    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError("Invalid token: subject claim missing.")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise AuthenticationError("Invalid token: malformed user identifier.")

    user = UserRepository.get_by_id(db, user_id)
    if not user or not user.is_active:
        logger.warning(f"Authentication failed: User {user_id} not found or inactive.")
        raise AuthenticationError("User not found or account disabled.")

    return user

def require_roles(*allowed_roles) -> Callable[[User], User]:
    """
    FastAPI dependency factory enforcing Role-Based Access Control (RBAC).
    Verifies that the authenticated user's current database role matches one of allowed_roles.
    """
    roles_set = set()
    for role in allowed_roles:
        if isinstance(role, (list, tuple, set)):
            roles_set.update(role)
        else:
            roles_set.add(role)

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role.name if current_user.role else ""
        if user_role not in roles_set:
            logger.warning(f"Authorization denied for user {current_user.id}: role '{user_role}' not in required roles {roles_set}")
            raise AuthorizationError("Access denied for this resource.")
        return current_user

    return role_checker
