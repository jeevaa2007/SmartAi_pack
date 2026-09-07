import pytest
from src.database.connection import SessionLocal

@pytest.fixture(scope="function")
def db_session():
    """
    Fixture providing a clean PostgreSQL database session for test isolation.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
