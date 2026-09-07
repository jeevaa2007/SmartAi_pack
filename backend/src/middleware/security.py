import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Appends standard secure headers to all HTTP responses to prevent clickjacking,
    mime-sniffing, and cross-site scripting vulnerabilities.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Attaches a unique Request-ID correlation token to incoming queries to allow
    cross-service audit tracing across logging files.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        # Extract existing header or generate a new unique token
        correlation_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Inject correlation token into logger contextual logs
        with logger.contextualize(request_id=correlation_id):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Expose tracking token in API response headers
            response.headers["X-Request-ID"] = correlation_id
            
            # Log request execution duration metrics
            logger.info(
                f"Request Executed: {request.method} {request.url.path} "
                f"status={response.status_code} latency={process_time:.4f}s"
            )
            return response
