"""Core app configuration."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Core application configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"
