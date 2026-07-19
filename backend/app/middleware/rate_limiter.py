"""
CrimeLens AI — Rate Limiter Middleware
========================================
In-memory sliding window rate limiter.
Tracks request counts per IP address within a configurable time window.
"""

import time
from collections import defaultdict
from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import get_settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Sliding window rate limiter that tracks requests per IP.
    Configurable via RATE_LIMIT_PER_MINUTE in settings.
    """

    def __init__(self, app):
        super().__init__(app)
        # {ip_address: [list of request timestamps]}
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._window_seconds: int = 60

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Check rate limit before processing request."""
        settings = get_settings()
        max_requests = settings.rate_limit_per_minute

        # Extract client IP (supports reverse proxy via X-Forwarded-For)
        client_ip = self._get_client_ip(request)
        now = time.time()

        # Clean up old timestamps outside the sliding window
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip]
            if now - ts < self._window_seconds
        ]

        # Check if limit exceeded
        if len(self._requests[client_ip]) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {max_requests} requests per minute.",
            )

        # Record this request
        self._requests[client_ip].append(now)

        # Add rate limit headers to response
        response = await call_next(request)
        remaining = max_requests - len(self._requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Window"] = f"{self._window_seconds}s"

        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP, respecting X-Forwarded-For for reverse proxies."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
