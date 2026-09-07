from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from typing import Any, Dict, List

class AppException(Exception):
    """
    Base exception for all custom domain errors.
    """
    def __init__(self, code: str, message: str, status_code: int = 400, details: Any = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details

class AuthenticationError(AppException):
    def __init__(self, message: str = "Invalid credentials or expired token.", details: Any = None):
        super().__init__(code="AUTHENTICATION_FAILED", message=message, status_code=401, details=details)

class AuthorizationError(AppException):
    def __init__(self, message: str = "Access denied for this resource.", details: Any = None):
        super().__init__(code="PERMISSION_DENIED", message=message, status_code=403, details=details)

class EntityNotFoundError(AppException):
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            code="ENTITY_NOT_FOUND",
            message=f"Requested {entity_name} with key '{identifier}' was not found.",
            status_code=404
        )

class RuleViolationException(AppException):
    def __init__(self, message: str, rule_code: str, details: Any = None):
        super().__init__(
            code=f"RULE_VIOLATION_{rule_code}",
            message=message,
            status_code=422,
            details=details
        )

def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers global exception hooks to capture validation, internal server, and custom domain exceptions,
    formatting them into a clean unified payload contract.
    """
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(f"Domain Exception Handled: [{exc.code}] {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = []
        for error in exc.errors():
            errors.append({
                "field": " -> ".join(map(str, error.get("loc", []))),
                "issue": error.get("msg", "Validation error occurred.")
            })
            
        logger.warning(f"Request Validation Failed for {request.url.path}: {errors}")
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Input validation failed on incoming request parameters.",
                    "details": errors
                }
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled Exception Intercepted on path {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please contact system administrators.",
                    "details": str(exc) if settings.ENVIRONMENT == "development" else None
                }
            }
        )
from src.core.config import settings
