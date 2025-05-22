from pathlib import Path
from datetime import timedelta
import os
import logging
import warnings
from dotenv import load_dotenv
from corsheaders.defaults import default_headers

# === ⚙️ Load Environment ===
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_ROOT = BASE_DIR / "prompt_sets"

# === ⚠️ Deprecation Warnings ===
warnings.filterwarnings("ignore", category=UserWarning, module="dj_rest_auth")

# === 🔐 Security ===
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-key")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

if not DEBUG and SECRET_KEY == "unsafe-secret-key":
    raise RuntimeError("❌ SECRET_KEY must be set securely in production!")

# === 🧩 Installed Apps ===
INSTALLED_APPS = [
    # Django Core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third Party
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "drf_spectacular",
    "django_extensions",
    "django_redis",
    # Local Apps
    "accounts.apps.AccountsConfig",
    "assistants",
    "agents",
    "embeddings",
    "mcp_core",
    "memory",
    "prompts",
    "characters",
    "images",
    "project",
    "story",
    "tts",
    "videos",
    "storyboard",
    "intel_core",
    "capabilities.dev_docs",
    "tools",
    "workflows",
    "metrics",
    "learning_loops",
    "simulation",
    "resources",
]

# === 🧵 Middleware ===
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "mcp_core.middleware.ApiVersionWarningMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# === 🧠 Templates ===
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ROOT_URLCONF = "server.urls"
WSGI_APPLICATION = "server.wsgi.application"

# === 🗃️ Database ===
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    }
}

# === 🛠️ Redis & Caching ===
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
            "PASSWORD": os.getenv("REDIS_PASSWORD", ""),
        },
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 3600
SESSION_SAVE_EVERY_REQUEST = True

# === 🔑 Authentication ===
AUTH_USER_MODEL = "accounts.CustomUser"

REST_AUTH = {
    "SIGNUP_FIELDS": {
        "username": {"required": True},
        "email": {"required": True},
    }
}
# Enable JWT support so dj-rest-auth login works with SIMPLE_JWT
REST_USE_JWT = True
# Store auth tokens in HttpOnly cookies so the frontend fetch helper can send
# credentials automatically
JWT_AUTH_COOKIE = "access"
JWT_AUTH_REFRESH_COOKIE = "refresh"

# === 🔐 JWT Config ===
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=24),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
}

# === 🔄 DRF Settings ===
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # Enable JWT auth via HttpOnly cookies. This allows the frontend to rely
        # on cookies set by dj-rest-auth without manually attaching the access
        # token in the Authorization header.
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "100/hour",
    },
}

# Optional: Turn off browsable API in production
if not DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
        "rest_framework.renderers.JSONRenderer"
    ]

# === 🌐 CORS ===
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True

# === 🪄 Celery ===
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "generate-interaction-summaries": {
        "task": "utils.tasks.generate_interaction_summaries",
        "schedule": crontab(minute="0", hour="*/6"),
    },
    "cleanup-redis-contexts": {
        "task": "utils.tasks.cleanup_redis_contexts",
        "schedule": crontab(minute="0", hour="*/12"),
    },
    "monitor-redis-usage": {
        "task": "utils.tasks.monitor_redis_usage",
        "schedule": crontab(minute="*/5"),
    },
    "generate-redis-report": {
        "task": "utils.tasks.generate_redis_report",
        "schedule": crontab(minute="0", hour="0"),
    },
    "check-redis-memory-usage": {
        "task": "utils.memory_tasks.check_redis_memory_usage",
        "schedule": crontab(minute="*/10"),
    },
    "analyze-redis-memory-growth": {
        "task": "utils.memory_tasks.analyze_redis_memory_growth",
        "schedule": crontab(minute="0", hour="*/1"),
    },
    "generate-redis-memory-report": {
        "task": "utils.memory_tasks.generate_redis_memory_report",
        "schedule": crontab(minute="30", hour="0"),
    },
    "cleanup-old-context-keys": {
        "task": "utils.memory_tasks.cleanup_old_context_keys",
        "schedule": crontab(minute="0", hour="2", day_of_week="mon,thu"),
        "kwargs": {"max_age_days": 7, "dry_run": False},
    },
    "evaluate-narrative-triggers": {
        "task": "storyboard.tasks.evaluate_narrative_triggers",
        "schedule": crontab(minute="*/5"),
    },
}

# === 🗂️ Static & Media ===
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# === 🧾 API Docs ===
SPECTACULAR_SETTINGS = {
    "TITLE": "Donkey AI Assistant API",
    "DESCRIPTION": "Flexible API for assistants, memory, prompts, and more.",
    "VERSION": "1.0.0",
    "SCHEMA_PATH_PREFIX": r"/api/",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_SPLIT_RESPONSE": True,
    "SECURITY": [
        {"Bearer": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}}
    ],
    "TAGS": [
        {"name": "auth", "description": "Authentication"},
        {"name": "assistants", "description": "Assistant tools"},
        {"name": "projects", "description": "Assistant projects"},
        {"name": "thoughts", "description": "Thought logs"},
        {"name": "memories", "description": "Memory systems"},
        {"name": "prompts", "description": "Prompt management"},
        {"name": "images", "description": "Image generation"},
        {"name": "characters", "description": "Character creation"},
        {"name": "embeddings", "description": "Embedding search"},
        {"name": "videos", "description": "Video generation"},
        {"name": "tts", "description": "TTS tools"},
    ],
    "SERVERS": [{"url": "/api", "description": "API base"}],
    "ERROR_RESPONSES": {
        "400": {"description": "Bad Request"},
        "401": {"description": "Unauthorized"},
        "403": {"description": "Forbidden"},
        "404": {"description": "Not Found"},
        "500": {"description": "Server Error"},
    },
    "EXAMPLES": True,
    "EXTENSIONS": {
        "x-logo": {"url": "/static/logo.png", "altText": "Donkey AI Assistant"},
        "x-support-email": "support@donkeybetz.com",
    },
    "POSTPROCESSING_HOOKS": ["drf_spectacular.hooks.postprocess_schema_enums"],
    "AUTHENTICATION_WHITELIST": [
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    ],
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "displayOperationId": True,
        "persistAuthorization": True,
        "syntaxHighlight.theme": "agate",
    },
    "SWAGGER_UI_DIST": "//unpkg.com/swagger-ui-dist@latest",
    "SWAGGER_UI_FAVICON_HREF": "//unpkg.com/swagger-ui-dist@latest/favicon-32x32.png",
    "REDOC_DIST": "//unpkg.com/redoc@latest/bundles/redoc.standalone.js",
}

# === 🪵 Logging ===
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

# === 🌐 Localization ===
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Denver"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
SITE_ID = 1

# Default token threshold for assistant delegation
ASSISTANT_DELEGATION_TOKEN_LIMIT = int(
    os.getenv("ASSISTANT_DELEGATION_TOKEN_LIMIT", "10000")
)
