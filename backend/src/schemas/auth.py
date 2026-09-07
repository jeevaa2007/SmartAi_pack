import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

class LoginRequest(BaseModel):
    """
    Client authentication login payload schema.
    Applies email normalization (trim whitespace + lowercase).
    """
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Email address cannot be empty.")
        return v.strip().lower()

class AuthenticatedUserResponse(BaseModel):
    """
    Safe public profile payload representation for authenticated users.
    Excludes sensitive fields such as password_hash.
    """
    id: uuid.UUID
    full_name: str
    email: str
    role: str
    store_id: Optional[uuid.UUID] = None
    is_active: bool
    is_verified: bool

    model_config = {
        "from_attributes": True
    }

class TokenData(BaseModel):
    """
    Authentication token response containing Bearer JWT token and user profile metadata.
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthenticatedUserResponse
