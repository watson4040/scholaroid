import os
from pathlib import Path

import dj_database_url
from decouple import config
from django.contrib.messages import constants as messages

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================================
# SECURITY
# ==========================================================

SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-temp-key-for-local-dev"
)

DEBUG = config(
    "DEBUG",
    default=False,
    cast=bool
)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,.railway.app"
).split(",")

CSRF_TRUSTED_ORIGINS = [
    origin
    for origin in config(
        "CSRF_TRUSTED_ORIGINS",
        default="https://*.railway.app"
    ).split(",")
    if origin
]

# ==========================================================
# CUSTOM USER
# ==========================================================

AUTH_USER_MODEL = "accountsApp.User"

SITE_ID = 1

# ==========================================================
# APPLICATIONS
# ==========================================================

INSTALLED_APPS = [

    # Third Party
    "jazzmin",
    "cloudinary",
    "cloudinary_storage",
    "channels",

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Local Apps
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

    # NEW
    "settingsApp",
    "schoolsApp",
    "payments",

    # Social Auth
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
# URLS
# ==========================================================

ROOT_URLCONF = "managementProject.urls"

WSGI_APPLICATION = "managementProject.wsgi.application"

ASGI_APPLICATION = "managementProject.asgi.application"

# ==========================================================
# TEMPLATES
# ==========================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

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


DATABASE_URL = config(
    "DATABASE_URL",
    default=None
)

if DATABASE_URL:

    try:

        DATABASES = {
            "default": dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
            )
        }

    except Exception as e:

        print(f"Database Error: {e}")

        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

else:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ==========================================================
# CHANNELS
# ==========================================================

REDIS_URL = config(
    "REDIS_URL",
    default=None
)

if REDIS_URL:

    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL]
            },
        }
    }

else:

    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }

# ==========================================================
# AUTHENTICATION
# ==========================================================

AUTHENTICATION_BACKENDS = [

    "social_core.backends.google.GoogleOAuth2",

    "django.contrib.auth.backends.ModelBackend",

]

LOGIN_URL = "login"

LOGIN_REDIRECT_URL = "/admin/"

LOGOUT_REDIRECT_URL = "home"

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config(
    "GOOGLE_OAUTH_CLIENT_ID",
    default=""
)

SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config(
    "GOOGLE_OAUTH_CLIENT_SECRET",
    default=""
)

SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    "prompt": "select_account"
}

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },

    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },

    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },

    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
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

TIME_ZONE = "UTC"

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

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# ==========================================================
# MEDIA FILES
# ==========================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

CLOUDINARY_URL = config(
    "CLOUDINARY_URL",
    default=""
)

if CLOUDINARY_URL:

    DEFAULT_FILE_STORAGE = (
        "cloudinary_storage.storage.MediaCloudinaryStorage"
    )

# ==========================================================
# EMAIL
# ==========================================================

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
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

SESSION_ENGINE = "django.contrib.sessions.backends.db"

WEBSOCKETS_ENABLED = config(
    "WEBSOCKETS_ENABLED",
    default=True,
    cast=bool,
)

# ==========================================================
# DEFAULT PRIMARY KEY
# ==========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==========================================================
# SECURITY (PRODUCTION)
# ==========================================================

if not DEBUG:

    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_BROWSER_XSS_FILTER = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    SECURE_HSTS_SECONDS = 31536000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True

    X_FRAME_OPTIONS = "DENY"

USE_X_FORWARDED_HOST = True

# ==========================================================
# JAZZMIN
# ==========================================================

JAZZMIN_SETTINGS = {

    "site_title": "Scholaroid Admin",

    "site_header": "Scholaroid",

    "site_brand": "Scholaroid School Management",

    "welcome_sign": "Welcome to Scholaroid School Management System",

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

    "topmenu_links": [

        {
            "name": "Dashboard",
            "url": "/dashboard/admin/",
            "permissions": ["auth.view_user"],
        },

        {
            "name": "Admin",
            "url": "admin:index",
            "permissions": ["auth.view_user"],
        },

    ],

    "icons": {

        "auth": "fas fa-users-cog",

        "accountsApp.User": "fas fa-user-shield",

        "studentsApp.Student": "fas fa-user-graduate",

        "teachersApp.Teacher": "fas fa-chalkboard-teacher",

        "parentsApp.Parent": "fas fa-people-roof",

        "classesApp.ClassRoom": "fas fa-school",

        "attendanceApp.Attendance": "fas fa-calendar-check",

        "feesApp.Fee": "fas fa-money-bill-wave",

        "examsApp.Exam": "fas fa-file-alt",

        "messagingApp.Message": "fas fa-envelope",

        "resourcesApp.Resource": "fas fa-book",

        "settingsApp.SchoolSettings": "fas fa-school",

        "settingsApp.Subscription": "fas fa-crown",

    },

}

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
# SCHOLAROID
# ==========================================================

SCHOLAROID = {

    "SYSTEM_NAME": "Scholaroid",

    "SYSTEM_VERSION": "1.0.0",

    "DEVELOPER": "Nexor Labs",

    "COPYRIGHT": "© Nexor Labs",

}