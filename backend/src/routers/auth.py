from typing import Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from src.api.deps import get_current_user
from src.database.connection import get_db
from src.models.user import User
from src.schemas.auth import AuthenticatedUserResponse, LoginRequest, TokenData
from src.schemas.response import APIResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=APIResponse[TokenData], summary="Authenticate user and issue JWT access token")
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
) -> APIResponse[TokenData]:
    """
    Authenticates user credentials against PostgreSQL, verifies password hash and account active state,
    records security audit events, and returns a signed Bearer JWT access token.
    """
    client_ip = request.client.host if request.client else None
    request_id = request.headers.get("X-Request-ID")

    token_data = AuthService.authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password,
        ip_address=client_ip,
        request_id=request_id
    )

    return APIResponse(success=True, data=token_data)

@router.get("/me", response_model=APIResponse[AuthenticatedUserResponse], summary="Fetch current authenticated user profile")
def get_me(
    current_user: User = Depends(get_current_user)
) -> APIResponse[AuthenticatedUserResponse]:
    """
    Retrieves the current authenticated user profile details using Bearer JWT authentication.
    Excludes password_hash and internal security parameters.
    """
    role_name = current_user.role.name if current_user.role else "OPERATOR"
    profile = AuthenticatedUserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        role=role_name,
        store_id=current_user.store_id,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified
    )
    return APIResponse(success=True, data=profile)
