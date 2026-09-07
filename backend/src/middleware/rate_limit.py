import time
from collections import defaultdict
from typing import Dict
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from src.core.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Lightweight, in-memory sliding window rate limiter middleware.
    Tracks client IP request rates and returns 429 Too Many Requests if quota is exceeded.
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = getattr(settings, "RATE_LIMIT_PER_MINUTE", requests_per_minute)
        # Store IP -> list of timestamps
        self.client_records: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Exempt health check probes from rate limiting
        if request.url.path.startswith(f"{settings.API_V1_STR}/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - 60.0

        # Clean timestamps older than 60 seconds
        timestamps = [ts for ts in self.client_records[client_ip] if ts > window_start]
        self.client_records[client_ip] = timestamps

        if len(timestamps) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip} on path: {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                        "details": [{"ip": client_ip, "limit": self.requests_per_minute, "window_seconds": 60}]
                    }
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                }
            )

        # Record this request
        self.client_records[client_ip].append(now)

        response = await call_next(request)
        remaining = max(0, self.requests_per_minute - len(self.client_records[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
