"""Ingest app configuration."""

from django.apps import AppConfig


class IngestConfig(AppConfig):
    """Ingest application configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ingest"
    verbose_name = "Data Ingestion"
