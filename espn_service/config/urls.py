"""URL configuration for espn_service project."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.core.views import HealthCheckView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Health check
    path("healthz", HealthCheckView.as_view(), name="health-check"),
    # API v1
    path("api/v1/", include("apps.espn.urls")),
    path("api/v1/ingest/", include("apps.ingest.urls")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
