"""Core middleware for request handling."""

import time
import uuid
from typing import Callable

import structlog
from django.http import HttpRequest, HttpResponse

logger = structlog.get_logger(__name__)


class RequestIDMiddleware:
    """Add unique request ID to each request for tracing."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.request_id = request_id  # type: ignore[attr-defined]

        # Bind request ID to structlog context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = self.get_response(request)

        # Add request ID to response headers
        response["X-Request-ID"] = request_id

        return response


class StructuredLoggingMiddleware:
    """Log request/response information in a structured format."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Skip logging for health checks
        if request.path == "/healthz":
            return self.get_response(request)

        start_time = time.perf_counter()

        # Log incoming request
        logger.info(
            "request_started",
            method=request.method,
            path=request.path,
            query_params=dict(request.GET),
            user_agent=request.headers.get("User-Agent", ""),
        )

        response = self.get_response(request)

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log response
        logger.info(
            "request_finished",
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        return response
