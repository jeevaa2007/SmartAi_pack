import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from src.models.user import User

class UserRepository:
    """
    Data repository handling User model persistence operations.
    """

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """
        Retrieves a user by normalized email address, eager loading their security Role relationship.
        """
        normalized_email = email.strip().lower()
        return (
            db.query(User)
            .options(joinedload(User.role))
            .filter(User.email == normalized_email)
            .first()
        )

    @staticmethod
    def get_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
        """
        Retrieves a user by UUID primary key, eager loading their security Role relationship.
        """
        return (
            db.query(User)
            .options(joinedload(User.role))
            .filter(User.id == user_id)
            .first()
        )

    @staticmethod
    def update_last_login(db: Session, user_id: uuid.UUID) -> None:
        """
        Updates the last_login_at timestamp for an authenticated user to current UTC time.
        """
        db.query(User).filter(User.id == user_id).update(
            {"last_login_at": datetime.now(timezone.utc)},
            synchronize_session=False
        )
        db.commit()
