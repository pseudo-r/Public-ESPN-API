"""Core views including health checks."""

from django.db import connection
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Health check endpoint for container orchestration."""

    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=["Health"],
        summary="Health check",
        description="Check service health and database connectivity.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "healthy"},
                    "database": {"type": "string", "example": "connected"},
                },
            },
            503: {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "unhealthy"},
                    "database": {"type": "string", "example": "disconnected"},
                    "error": {"type": "string"},
                },
            },
        },
    )
    def get(self, request: Request) -> Response:
        """Return health status including database connectivity."""
        health_status = {
            "status": "healthy",
            "database": "connected",
        }

        try:
            # Check database connectivity
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["database"] = "disconnected"
            health_status["error"] = str(e)
            return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(health_status, status=status.HTTP_200_OK)
