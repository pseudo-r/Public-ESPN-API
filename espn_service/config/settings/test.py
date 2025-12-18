"""Test settings."""

from .base import *  # noqa: F401, F403

DEBUG = False

# Use in-memory SQLite for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Cache - Use dummy cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Celery - Always eager for tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Logging - Reduce noise during tests
LOGGING["root"]["level"] = "WARNING"  # noqa: F405
for logger in LOGGING["loggers"].values():  # noqa: F405
    logger["level"] = "WARNING"

# Faster static files handling
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# ESPN Client - Use test configuration
ESPN_CLIENT = {
    "SITE_API_BASE_URL": "https://site.api.espn.com",
    "CORE_API_BASE_URL": "https://sports.core.api.espn.com",
    "TIMEOUT": 5.0,
    "MAX_RETRIES": 1,
    "RETRY_BACKOFF": 0.1,
    "USER_AGENT": "ESPN-Service-Test/1.0",
    "RATE_LIMIT_REQUESTS": 1000,
    "RATE_LIMIT_PERIOD": 60,
}
