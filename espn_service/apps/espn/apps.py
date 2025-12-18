"""ESPN app configuration."""

from django.apps import AppConfig


class ESPNConfig(AppConfig):
    """ESPN application configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.espn"
    verbose_name = "ESPN"
