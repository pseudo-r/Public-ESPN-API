"""Production settings."""

from .base import *  # noqa: F401, F403

DEBUG = False

# Security settings
SECRET_KEY = env("SECRET_KEY")  # noqa: F405
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # noqa: F405

# HTTPS settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database - PostgreSQL required
DATABASES = {
    "default": env.db("DATABASE_URL"),  # noqa: F405
}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DATABASE_CONN_MAX_AGE", default=60)  # noqa: F405
DATABASES["default"]["OPTIONS"] = {
    "connect_timeout": 10,
}

# Cache - Redis required
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://redis:6379/1"),  # noqa: F405
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "RETRY_ON_TIMEOUT": True,
        },
    }
}

# Logging - JSON format for production
LOGGING["handlers"]["console"]["formatter"] = "json"  # noqa: F405
LOGGING["root"]["level"] = "INFO"  # noqa: F405
for logger in LOGGING["loggers"].values():  # noqa: F405
    logger["handlers"] = ["json"]

# CORS - Restrict to allowed origins
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])  # noqa: F405

# Celery
CELERY_TASK_ALWAYS_EAGER = False
CELERY_BROKER_URL = env("CELERY_BROKER_URL")  # noqa: F405
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")  # noqa: F405

# Static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Email - Use SMTP in production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="")  # noqa: F405
EMAIL_PORT = env.int("EMAIL_PORT", default=587)  # noqa: F405
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")  # noqa: F405
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")  # noqa: F405

# Sentry integration (optional)
SENTRY_DSN = env("SENTRY_DSN", default="")  # noqa: F405
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.1),  # noqa: F405
        send_default_pii=False,
        environment=env("ENVIRONMENT", default="production"),  # noqa: F405
    )
