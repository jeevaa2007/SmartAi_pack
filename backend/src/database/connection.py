import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from loguru import logger
from src.core.config import settings

# Determine final connection URL based on configuration and environments
db_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)

logger.info(f"Initializing database engine on context: {db_url.split('@')[-1] if '@' in db_url else db_url}")

# Set database engine configurations
connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}

try:
    engine = create_engine(
        db_url,
        pool_pre_ping=True,      # Automatically verify stale connections
        connect_args=connect_args
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database session provider initialized successfully.")
except Exception as e:
    logger.critical(f"Failed to initialize database engine connection: {str(e)}")
    raise e

# Declarative Base for models definition
Base = declarative_base()

def get_db():
    """
    Generator function yielding a thread-local database session.
    Automatically closes session when request handling context returns.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

