import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application-wide environment variable validator and configuration settings.
    Uses Pydantic BaseSettings to automatically parse environment flags.
    """
    
    # Core
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "SmartPack AI"
    API_V1_STR: str = "/api/v1"
    
    # Server Interfaces
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Database Layer
    DATABASE_URL: str = "postgresql://smartpack_user:smartpack_password@db:5432/smartpack_db"
    LOCAL_DATABASE_URL: str = "sqlite:///./smartpack_local.db"
    
    # Security Configurations
    # Change in production configuration
    JWT_SECRET: str = "8f5db9cf2b4d89617ad565e3150244cf5ef02b1bcfa9b4a1b0235b2e9d7c01b2"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS policy origins
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Logging configurations
    LOG_LEVEL: str = "DEBUG"
    LOG_DIR: str = "./logs"
    LOG_ROTATION_SIZE: str = "50MB"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
