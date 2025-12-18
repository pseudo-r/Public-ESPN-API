"""Custom exception handling for the API."""

from typing import Any

import structlog
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = structlog.get_logger(__name__)


class ESPNServiceError(APIException):
    """Base exception for ESPN service errors."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An internal error occurred."
    default_code = "internal_error"


class ESPNClientError(ESPNServiceError):
    """Error communicating with ESPN API."""

    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "Error communicating with ESPN API."
    default_code = "espn_client_error"


class ESPNRateLimitError(ESPNClientError):
    """ESPN API rate limit exceeded."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "ESPN API rate limit exceeded. Please try again later."
    default_code = "espn_rate_limit"


class ESPNNotFoundError(ESPNClientError):
    """ESPN resource not found."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found in ESPN API."
    default_code = "espn_not_found"


class IngestionError(ESPNServiceError):
    """Error during data ingestion."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Error during data ingestion."
    default_code = "ingestion_error"


class ValidationError(ESPNServiceError):
    """Validation error for API requests."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid request data."
    default_code = "validation_error"


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Custom exception handler for DRF that adds structured error responses."""
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Log the exception
    logger.error(
        "api_exception",
        exc_type=type(exc).__name__,
        exc_message=str(exc),
        view=context.get("view").__class__.__name__ if context.get("view") else None,
    )

    if response is not None:
        # Enhance error response with structured format
        error_data = {
            "error": {
                "code": getattr(exc, "default_code", "error"),
                "message": str(exc.detail) if hasattr(exc, "detail") else str(exc),
                "status": response.status_code,
            }
        }

        # Add field errors for validation exceptions
        if hasattr(exc, "detail") and isinstance(exc.detail, dict):
            error_data["error"]["fields"] = exc.detail

        response.data = error_data
        return response

    # Handle Django-specific exceptions
    if isinstance(exc, Http404):
        return Response(
            {
                "error": {
                    "code": "not_found",
                    "message": "Resource not found.",
                    "status": 404,
                }
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, DjangoValidationError):
        return Response(
            {
                "error": {
                    "code": "validation_error",
                    "message": str(exc),
                    "status": 400,
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # For unhandled exceptions, return a generic error
    logger.exception("unhandled_exception", exc=exc)
    return Response(
        {
            "error": {
                "code": "internal_error",
                "message": "An internal error occurred.",
                "status": 500,
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
