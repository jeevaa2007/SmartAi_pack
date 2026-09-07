from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from loguru import logger

from src.core.config import settings
from src.core.logging_config import setup_logging
from src.core.exceptions import register_exception_handlers
from src.database.connection import get_db, engine
from src.schemas.response import APIResponse
from src.middleware.security import SecurityHeadersMiddleware, CorrelationIdMiddleware
from src.middleware.rate_limit import RateLimitMiddleware
from src.routers.auth import router as auth_router
from src.routers.stores import router as stores_router
from src.routers.products import router as products_router
from src.routers.operators import router as operators_router
from src.routers.packaging import router as packaging_router
from src.routers.orders import router as orders_router
from src.routers.packing_verification import router as verification_router
from src.routers.dashboard import router as dashboard_router

# Initialize logging framework
setup_logging()

# Instantiate FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise API Gateway for AI-Powered Packing Quality Verification",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Apply CORS Policy configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Custom Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RateLimitMiddleware)

# Register custom exception handler middleware mapping standard responses
register_exception_handlers(app)

# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(stores_router, prefix=settings.API_V1_STR)
app.include_router(products_router, prefix=settings.API_V1_STR)
app.include_router(operators_router, prefix=settings.API_V1_STR)
app.include_router(packaging_router, prefix=settings.API_V1_STR)
app.include_router(orders_router, prefix=settings.API_V1_STR)
app.include_router(verification_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up SmartPack AI API services...")
    # Validate database connection availability
    try:
        connection = engine.connect()
        connection.close()
        logger.info("Database connectivity check: OK.")
    except Exception as e:
        logger.error(f"Database connectivity check: FAILED. Error: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down SmartPack AI API services...")

@app.get(f"{settings.API_V1_STR}/health/liveness", response_model=APIResponse[dict], tags=["System Health"])
def health_liveness():
    """
    Liveness probe verifying that the FastAPI gateway event loop is responsive.
    Crucial for container management (Kubernetes/Docker).
    """
    return APIResponse(
        success=True,
        data={
            "status": "alive",
            "environment": settings.ENVIRONMENT
        }
    )

@app.get(f"{settings.API_V1_STR}/health/readiness", response_model=APIResponse[dict], tags=["System Health"])
def health_readiness(db: Session = Depends(get_db)):
    """
    Readiness probe validating that backend dependencies (Database, etc.) are available.
    """
    db_status = "healthy"
    try:
        # Verify db session query loop
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Readiness check failed database check: {str(e)}")
        db_status = "unhealthy"
        
    status = "ready" if db_status == "healthy" else "degraded"
    
    return APIResponse(
        success=status == "ready",
        data={
            "status": status,
            "services": {
                "api": "healthy",
                "database": db_status
            }
        }
    )
