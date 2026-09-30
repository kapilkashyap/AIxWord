"""
Custom middleware for FastAPI application.

This module provides custom middleware components for the AIxWord API,
including request logging, timing, error tracking, and request ID generation.
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.

    This middleware logs:
    - Request method, path, and query parameters
    - Request headers (excluding sensitive data)
    - Response status code
    - Request processing time
    - Request ID for tracing

    Each request is assigned a unique ID that can be used for tracing
    through logs and debugging.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and log details.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Add request ID to request state for access in handlers
        request.state.request_id = request_id

        # Log request details
        start_time = time.time()

        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"[ID: {request_id}]"
        )

        # Log query parameters if present
        if request.url.query:
            logger.debug(f"Query params: {request.url.query} [ID: {request_id}]")

        # Process request
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"

            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"[Status: {response.status_code}] "
                f"[Time: {process_time:.4f}s] "
                f"[ID: {request_id}]"
            )

            return response

        except Exception as exc:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"[Error: {str(exc)}] "
                f"[Time: {process_time:.4f}s] "
                f"[ID: {request_id}]",
                exc_info=True
            )
            raise


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking request timing metrics.

    This middleware measures the time taken to process each request
    and adds timing information to response headers.

    Headers added:
    - X-Process-Time: Time in seconds to process the request
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add timing information.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response with timing headers
        """
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers to responses.

    This middleware adds common security headers to all responses:
    - X-Content-Type-Options: Prevent MIME type sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: Enable XSS filtering (legacy browsers)
    - Strict-Transport-Security: Enforce HTTPS (if enabled)
    """

    def __init__(self, app: ASGIApp, enable_hsts: bool = False):
        """
        Initialize security headers middleware.

        Args:
            app: ASGI application
            enable_hsts: Whether to enable HSTS (only for HTTPS)
        """
        super().__init__(app)
        self.enable_hsts = enable_hsts

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add security headers.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response with security headers
        """
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Add HSTS if enabled (only for production HTTPS)
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response


class RateLimitInfo:
    """
    Simple rate limit tracking (in-memory).

    Note: This is a basic implementation for demonstration.
    For production, use a proper rate limiting solution like
    slowapi or redis-based rate limiting.
    """

    def __init__(self):
        """Initialize rate limit tracker."""
        self._requests: dict[str, list[float]] = {}

    def check_rate_limit(
        self,
        client_id: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> tuple[bool, int]:
        """
        Check if client has exceeded rate limit.

        Args:
            client_id: Client identifier (IP address, API key, etc.)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        current_time = time.time()
        window_start = current_time - window_seconds

        # Get or create request list for client
        if client_id not in self._requests:
            self._requests[client_id] = []

        # Remove old requests outside window
        self._requests[client_id] = [
            req_time for req_time in self._requests[client_id]
            if req_time > window_start
        ]

        # Check if limit exceeded
        request_count = len(self._requests[client_id])
        is_allowed = request_count < max_requests
        remaining = max(0, max_requests - request_count - 1)

        # Add current request if allowed
        if is_allowed:
            self._requests[client_id].append(current_time)

        return is_allowed, remaining


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for basic rate limiting.

    This is a simple in-memory rate limiter for demonstration.
    For production, use a proper distributed rate limiting solution.

    Limits are applied per client IP address.
    """

    def __init__(
        self,
        app: ASGIApp,
        max_requests: int = 100,
        window_seconds: int = 60
    ):
        """
        Initialize rate limit middleware.

        Args:
            app: ASGI application
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.rate_limiter = RateLimitInfo()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and enforce rate limits.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response or 429 Too Many Requests
        """
        # Get client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        is_allowed, remaining = self.rate_limiter.check_rate_limit(
            client_ip,
            self.max_requests,
            self.window_seconds
        )

        if not is_allowed:
            # Rate limit exceeded
            logger.warning(
                f"Rate limit exceeded for client {client_ip} "
                f"on {request.method} {request.url.path}"
            )

            return Response(
                content='{"error": "Rate limit exceeded", "message": "Too many requests"}',
                status_code=429,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + self.window_seconds)),
                    "Retry-After": str(self.window_seconds),
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time() + self.window_seconds)
        )

        return response


def get_request_id(request: Request) -> str:
    """
    Get the request ID from request state.

    This function retrieves the request ID that was set by the
    RequestLoggingMiddleware. If no ID is found, generates a new one.

    Args:
        request: FastAPI request object

    Returns:
        Request ID string
    """
    if hasattr(request.state, "request_id"):
        return request.state.request_id
    return str(uuid.uuid4())
