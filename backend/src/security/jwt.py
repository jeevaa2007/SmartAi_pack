import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
from jose import JWTError, jwt
from loguru import logger
from src.core.config import settings
from src.core.exceptions import AuthenticationError

def create_access_token(
    subject: Union[str, uuid.UUID],
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Encodes and signs a JWT access token using configured algorithm and secret.
    Claims include sub (user UUID), role, exp (expiration timestamp), and iat (issued-at).
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "role": str(role),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
    }

    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to generate JWT access token: {str(e)}")
        raise AuthenticationError("Could not generate authentication token.")

def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates incoming JWT access tokens against configured secret and algorithm.
    Validates token signature, expiration (exp), and subject (sub) payload.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        subject: Optional[str] = payload.get("sub")
        if not subject:
            raise AuthenticationError("Invalid authentication token: missing subject claim.")
        return payload
    except JWTError as exc:
        logger.warning(f"JWT validation failed: {str(exc)}")
        raise AuthenticationError("Invalid, expired, or malformed authentication token.")
    except Exception as exc:
        logger.warning(f"Unexpected token decoding error: {str(exc)}")
        raise AuthenticationError("Invalid authentication token.")

