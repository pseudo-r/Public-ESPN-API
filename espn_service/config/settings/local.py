"""Local development settings."""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Database - PostgreSQL on Fedora server, fallback to SQLite if unavailable
DATABASES = {
    "default": env.db(  # noqa: F405
        "DATABASE_URL",
        default="sqlite:///db.sqlite3",
    ),
}

# CORS - Allow all in development
CORS_ALLOW_ALL_ORIGINS = True

# Cache - Redis on Fedora server, fallback to local memory
CACHES = {
    "default": env.cache(  # noqa: F405
        "CACHE_URL",
        default="locmemcache://",
    ),
}

# Add browsable API renderer in development
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# Logging - Console output with colors
LOGGING["handlers"]["console"]["formatter"] = "console"  # noqa: F405
LOGGING["root"]["level"] = "DEBUG"  # noqa: F405

# Email - Console backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Celery - Use Redis on Fedora server
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)  # noqa: F405
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")  # noqa: F405
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")  # noqa: F405
