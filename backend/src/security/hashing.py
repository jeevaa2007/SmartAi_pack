import bcrypt
import passlib.handlers.bcrypt

# Passlib compatibility patch for bcrypt >= 4.0.0
if not hasattr(bcrypt, "__about__"):
    class BcryptAbout:
        __version__ = getattr(bcrypt, "__version__", "4.0.0")
    bcrypt.__about__ = BcryptAbout()

orig_detect_wrap_bug = getattr(passlib.handlers.bcrypt, "detect_wrap_bug", None)
if orig_detect_wrap_bug:
    def safe_detect_wrap_bug(ident):
        try:
            return orig_detect_wrap_bug(ident)
        except ValueError:
            return False
    passlib.handlers.bcrypt.detect_wrap_bug = safe_detect_wrap_bug

from passlib.context import CryptContext

# Set up bcrypt crypt context for secure password hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a stored bcrypt hash.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generates a secure bcrypt password hash.
    """
    return pwd_context.hash(password)
