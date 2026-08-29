
import os
from pathlib import Path

import dj_database_url
from decouple import config
from django.contrib.messages import constants as messages


# ==========================================================
# BASE DIRECTORY
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================================
# ENVIRONMENT
# ==========================================================
#
# Production is the default.
#
# IMPORTANT:
# Render should have:
#
#     DEBUG=False
#
# in its Environment Variables.
#
# Local development can explicitly use:
#
#     DEBUG=True
#
# ==========================================================

DEBUG = config(
    "DEBUG",
    default=False,
    cast=bool,
)


# ==========================================================
# SECRET KEY
# ==========================================================
#
# In production, SECRET_KEY should ALWAYS be configured
# through the environment.
#
# The fallback exists only to prevent configuration errors
# during local development.
# ==========================================================

SECRET_KEY = config(
    "SECRET_KEY",
    default=(
        "django-insecure-local-development-key-"
        "change-this-in-production"
    ),
)


# ==========================================================
# ALLOWED HOSTS
# ==========================================================

_default_allowed_hosts = (
    "localhost,"
    "127.0.0.1,"
    "[::1],"
    ".onrender.com,"
    ".railway.app"
)

ALLOWED_HOSTS = [
    host.strip()
    for host in config(
        "ALLOWED_HOSTS",
        default=_default_allowed_hosts,
    ).split(",")
    if host.strip()
]


# ==========================================================
# CSRF TRUSTED ORIGINS
# ==========================================================
#
# Render uses HTTPS.
#
# The production Render domain should be configured in the
# Render environment variables as:
#
# CSRF_TRUSTED_ORIGINS=https://scholaroid.onrender.com
#
# Multiple origins can be separated by commas.
# ==========================================================

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]


configured_csrf_origins = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
)


if configured_csrf_origins:

    CSRF_TRUSTED_ORIGINS.extend(
        origin.strip()
        for origin in configured_csrf_origins.split(",")
        if origin.strip()
    )


CSRF_TRUSTED_ORIGINS = list(
    dict.fromkeys(
        CSRF_TRUSTED_ORIGINS
    )
)


# ==========================================================
# CUSTOM USER MODEL
# ==========================================================

AUTH_USER_MODEL = "accountsApp.User"

SITE_ID = 1


# ==========================================================
# APPLICATIONS
# ==========================================================

INSTALLED_APPS = [

    # ------------------------------------------------------
    # Third-party applications
    # ------------------------------------------------------

    "jazzmin",
    "cloudinary",
    "cloudinary_storage",
    "channels",

    # ------------------------------------------------------
    # Django applications
    # ------------------------------------------------------

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # ------------------------------------------------------
    # Scholaroid applications
    # ------------------------------------------------------

    "accountsApp",
    "classesApp",
    "studentsApp",
    "teachersApp",
    "parentsApp",
    "attendanceApp",
    "examsApp",
    "messagingApp",
    "feesApp",
    "resourcesApp",
    "settingsApp",
    "schoolsApp",
    "payments",

    # ------------------------------------------------------
    # Social authentication
    # ------------------------------------------------------

    "social_django",
]


# ==========================================================
# MIDDLEWARE
# ==========================================================

MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",

    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "social_django.middleware.SocialAuthExceptionMiddleware",
]


# ==========================================================
# URL CONFIGURATION
# ==========================================================

ROOT_URLCONF = "managementProject.urls"


# ==========================================================
# WSGI
# ==========================================================

WSGI_APPLICATION = "managementProject.wsgi.application"


# ==========================================================
# ASGI
# ==========================================================

ASGI_APPLICATION = "managementProject.asgi.application"


# ==========================================================
# TEMPLATES
# ==========================================================

TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends.django.DjangoTemplates"
        ),

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",

                "social_django.context_processors.backends",

                "social_django.context_processors.login_redirect",
            ],
        },
    },
]


# ==========================================================
# DATABASE
# ==========================================================
#
# PRODUCTION:
#
# DATABASE_URL must point to your Supabase PostgreSQL
# database.
#
# LOCAL:
#
# When DEBUG=True and DATABASE_URL is absent, SQLite is used.
#
# IMPORTANT:
# We do NOT silently fall back to SQLite when DEBUG=False.
# ==========================================================

DATABASE_URL = config(
    "DATABASE_URL",
    default="",
)


if DATABASE_URL:

    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
        )
    }

    # ------------------------------------------------------
    # PostgreSQL connection options
    # ------------------------------------------------------
    #
    # Supabase PostgreSQL normally requires SSL.
    #
    # Do not disable SSL in production.
    #
    # When DEBUG=True, local PostgreSQL installations may
    # not support SSL, so SSL is disabled only for local
    # development.
    # ------------------------------------------------------

    if DEBUG:

        DATABASES["default"].setdefault(
            "OPTIONS",
            {},
        )

        DATABASES["default"]["OPTIONS"].setdefault(
            "sslmode",
            "disable",
        )

    else:

        DATABASES["default"].setdefault(
            "OPTIONS",
            {},
        )

        DATABASES["default"]["OPTIONS"].setdefault(
            "sslmode",
            "require",
        )

else:

    if DEBUG:

        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

    else:

        raise RuntimeError(
            "DATABASE_URL is required when DEBUG=False. "
            "Configure the Supabase PostgreSQL DATABASE_URL "
            "in the Render environment variables."
        )


# ==========================================================
# CHANNELS / REDIS
# ==========================================================

REDIS_URL = config(
    "REDIS_URL",
    default="",
)


if REDIS_URL:

    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": (
                "channels_redis.core.RedisChannelLayer"
            ),

            "CONFIG": {
                "hosts": [
                    REDIS_URL
                ],
            },
        }
    }

else:

    # ------------------------------------------------------
    # Fallback channel layer.
    #
    # This is acceptable when Redis is not configured, but
    # it does not provide multi-process/persistent messaging.
    # ------------------------------------------------------

    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": (
                "channels.layers.InMemoryChannelLayer"
            ),
        }
    }


# ==========================================================
# AUTHENTICATION BACKENDS
# ==========================================================

AUTHENTICATION_BACKENDS = [

    "social_core.backends.google.GoogleOAuth2",

    "django.contrib.auth.backends.ModelBackend",
]


# ==========================================================
# LOGIN / LOGOUT
# ==========================================================

LOGIN_URL = "login"

LOGIN_REDIRECT_URL = "/admin/"

LOGOUT_REDIRECT_URL = "home"


# ==========================================================
# GOOGLE OAUTH
# ==========================================================

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config(
    "GOOGLE_OAUTH_CLIENT_ID",
    default="",
)


SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config(
    "GOOGLE_OAUTH_CLIENT_SECRET",
    default="",
)


SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    "prompt": "select_account",
}


# ==========================================================
# PASSWORD VALIDATORS
# ==========================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ==========================================================
# MESSAGE TAGS
# ==========================================================

MESSAGE_TAGS = {

    messages.DEBUG: "secondary",

    messages.INFO: "info",

    messages.SUCCESS: "success",

    messages.WARNING: "warning",

    messages.ERROR: "danger",
}


# ==========================================================
# INTERNATIONALIZATION
# ==========================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Lusaka"

USE_I18N = True

USE_TZ = True


# ==========================================================
# STATIC FILES
# ==========================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# ==========================================================
# WHITENOISE
# ==========================================================

STORAGES = {

    "default": {
        "BACKEND": (
            "django.core.files.storage."
            "FileSystemStorage"
        ),
    },

    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


# ==========================================================
# MEDIA FILES
# ==========================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ==========================================================
# CLOUDINARY
# ==========================================================

CLOUDINARY_URL = config(
    "CLOUDINARY_URL",
    default="",
)


if CLOUDINARY_URL:

    DEFAULT_FILE_STORAGE = (
        "cloudinary_storage.storage."
        "MediaCloudinaryStorage"
    )


# ==========================================================
# EMAIL
# ==========================================================

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default=(
        "django.core.mail.backends.console.EmailBackend"
    ),
)


DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default="Scholaroid <noreply@scholaroid.com>",
)


EMAIL_HOST = config(
    "EMAIL_HOST",
    default="",
)


EMAIL_PORT = config(
    "EMAIL_PORT",
    default=587,
    cast=int,
)


EMAIL_HOST_USER = config(
    "EMAIL_HOST_USER",
    default="",
)


EMAIL_HOST_PASSWORD = config(
    "EMAIL_HOST_PASSWORD",
    default="",
)


EMAIL_USE_TLS = config(
    "EMAIL_USE_TLS",
    default=True,
    cast=bool,
)


# ==========================================================
# SESSION
# ==========================================================

SESSION_ENGINE = (
    "django.contrib.sessions.backends.db"
)


# ==========================================================
# WEBSOCKETS
# ==========================================================

WEBSOCKETS_ENABLED = config(
    "WEBSOCKETS_ENABLED",
    default=True,
    cast=bool,
)


# ==========================================================
# DEFAULT PRIMARY KEY
# ==========================================================

DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)


# ==========================================================
# SECURITY CONFIGURATION
# ==========================================================

if DEBUG:

    # ------------------------------------------------------
    # LOCAL DEVELOPMENT
    # ------------------------------------------------------

    SECURE_SSL_REDIRECT = False

    SESSION_COOKIE_SECURE = False

    CSRF_COOKIE_SECURE = False

    SECURE_PROXY_SSL_HEADER = None

    SECURE_HSTS_SECONDS = 0

    SECURE_HSTS_INCLUDE_SUBDOMAINS = False

    SECURE_HSTS_PRELOAD = False

    SECURE_SSL_HOST = None

    USE_X_FORWARDED_HOST = False

    SESSION_COOKIE_HTTPONLY = True

    CSRF_COOKIE_HTTPONLY = False

else:

    # ------------------------------------------------------
    # PRODUCTION / RENDER HTTPS
    # ------------------------------------------------------

    # Render terminates HTTPS at its proxy and forwards the
    # original protocol through X-Forwarded-Proto.

    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SESSION_COOKIE_HTTPONLY = True

    CSRF_COOKIE_HTTPONLY = False

    SECURE_HSTS_SECONDS = 31536000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = "DENY"

    USE_X_FORWARDED_HOST = True


# ==========================================================
# DJANGO ERROR LOGGING
# ==========================================================
#
# IMPORTANT:
#
# DEBUG remains FALSE in production.
#
# This logging configuration sends Django ERROR-level
# exceptions to stdout/stderr so Render captures the actual
# traceback in its Logs.
#
# We are NOT enabling DEBUG=True merely to see errors.
# ==========================================================

LOGGING = {

    "version": 1,

    "disable_existing_loggers": False,

    "formatters": {

        "django.server": {
            "format": (
                "{asctime} {levelname} "
                "{name} {message}"
            ),
            "style": "{",
        },

    },

    "handlers": {

        "console": {
            "class": "logging.StreamHandler",
        },

    },

    "loggers": {

        "django": {
            "handlers": [
                "console"
            ],
            "level": "ERROR",
            "propagate": False,
        },

        "django.request": {
            "handlers": [
                "console"
            ],
            "level": "ERROR",
            "propagate": False,
        },

        "django.server": {
            "handlers": [
                "console"
            ],
            "level": "ERROR",
            "propagate": False,
        },

    },
}


# ==========================================================
# JAZZMIN ADMIN
# ==========================================================

JAZZMIN_SETTINGS = {

    "site_title": "Scholaroid Admin",

    "site_header": "Scholaroid",

    "site_brand": "Scholaroid School Management",

    "welcome_sign": (
        "Welcome to Scholaroid School Management System"
    ),

    "copyright": "© Nexor Labs",

    "show_sidebar": True,

    "navigation_expanded": True,

    "sidebar_fixed": True,

    "navbar_fixed": True,

    "footer_fixed": True,

    "navigation_sticky": True,

    "navbar_sticky": True,

    "related_modal_active": True,

    "changeform_format": "horizontal_tabs",

    # ------------------------------------------------------
    # JAZZMIN TOP MENU
    # ------------------------------------------------------

    "topmenu_links": [

        {
            "name": "Dashboard",

            "url": "/dashboard/admin/",

            "permissions": [
                "auth.view_user"
            ],
        },

        {
            "name": "Admin",

            "url": "admin:index",

            "permissions": [
                "auth.view_user"
            ],
        },
    ],

    # ------------------------------------------------------
    # JAZZMIN ICONS
    # ------------------------------------------------------

    "icons": {

        "auth": "fas fa-users-cog",

        "accountsApp.User": (
            "fas fa-user-shield"
        ),

        "studentsApp.Student": (
            "fas fa-user-graduate"
        ),

        "teachersApp.Teacher": (
            "fas fa-chalkboard-teacher"
        ),

        "parentsApp.Parent": (
            "fas fa-people-roof"
        ),

        "classesApp.ClassRoom": (
            "fas fa-school"
        ),

        "attendanceApp.Attendance": (
            "fas fa-calendar-check"
        ),

        "feesApp.Fee": (
            "fas fa-money-bill-wave"
        ),

        "examsApp.Exam": (
            "fas fa-file-alt"
        ),

        "messagingApp.Message": (
            "fas fa-envelope"
        ),

        "resourcesApp.Resource": (
            "fas fa-book"
        ),

        "settingsApp.SchoolSettings": (
            "fas fa-school"
        ),

        "settingsApp.Subscription": (
            "fas fa-crown"
        ),
    },
}


# ==========================================================
# JAZZMIN UI TWEAKS
# ==========================================================

JAZZMIN_UI_TWEAKS = {

    "theme": "flatly",

    "dark_mode_theme": "darkly",

    "navbar": "navbar-primary",

    "sidebar": "sidebar-dark-primary",

    "brand_colour": "navbar-primary",

    "accent": "accent-primary",

    "navbar_small_text": False,

    "footer_small_text": False,

    "sidebar_nav_small_text": False,

    "sidebar_disable_expand": False,

    "sidebar_nav_child_indent": True,

    "sidebar_nav_compact_style": False,

    "sidebar_nav_legacy_style": False,

    "actions_sticky_top": True,
}


# ==========================================================
# SCHOLAROID SYSTEM CONFIGURATION
# ==========================================================

SCHOLAROID = {

    "SYSTEM_NAME": "Scholaroid",

    "SYSTEM_VERSION": "1.0.0",

    "DEVELOPER": "Nexor Labs",

    "COPYRIGHT": "© Nexor Labs",
}
