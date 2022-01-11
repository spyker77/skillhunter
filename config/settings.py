import ast
import os
from pathlib import Path
from typing import Dict, List, Union

import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

ENVIRONMENT = os.getenv("ENVIRONMENT", default="production")


# Quick-start development settings - unsuitable for production
# https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ast.literal_eval(os.getenv("DEBUG", default="False"))


ALLOWED_HOSTS = [
    "skillhunter.app",
    "3.125.98.119",
    "localhost",
    "127.0.0.1",
]

SITE_ID = 1

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    # Local apps
    "resume_analyzer",
    "scrapers",
    "pages",
    "api",
    "fast_api",
    # 3rd party apps
    "debug_toolbar",
    "rest_framework",
    "drf_spectacular",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [BASE_DIR / "templates/jinja2"],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "config.jinja2.environment",
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# Keep connection to the database opened for 6 hours in order
# to prevent associated errors due to its early close when scraping.
CONN_MAX_AGE = 60 * 60 * 6

DATABASES = {"default": dj_database_url.config(default="postgres://postgres@db/postgres", conn_max_age=CONN_MAX_AGE)}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", default="redis://redis:6379"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Permissions-Policy settings
# https://github.com/adamchainz/django-permissions-policy
PERMISSIONS_POLICY: Dict[str, Union[str, List[str]]] = {
    "accelerometer": [],
    "ambient-light-sensor": [],
    "autoplay": [],
    "camera": [],
    "document-domain": [],
    "encrypted-media": [],
    "fullscreen": [],
    "geolocation": [],
    "gyroscope": [],
    "magnetometer": [],
    "microphone": [],
    "midi": [],
    "payment": [],
    "sync-xhr": [],
    "usb": [],
}


# Content-Security-Policy settings
# https://django-csp.readthedocs.io/en/latest/
CSP_DEFAULT_SRC = ["'self'"]
CSP_STYLE_SRC = ["'self'", "https://unpkg.com"]
CSP_SCRIPT_SRC = ["'self'", "https://unpkg.com"]
CSP_FONT_SRC = ["'self'"]
CSP_IMG_SRC = ["'self'", "data:"]
CSP_INCLUDE_NONCE_IN = ["script-src"]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
USE_S3 = ast.literal_eval(os.getenv("USE_S3", default="False"))

if USE_S3:
    # AWS S3 storage settings
    AWS_DEFAULT_ACL = None
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
    AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN", "")
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=2592000"}
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    # Static files
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    STATICFILES_STORAGE = "config.storage_backends.StaticStorage"
    # Media files
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
    DEFAULT_FILE_STORAGE = "config.storage_backends.MediaStorage"
    # Extend Content-Security-Policy
    CSP_STYLE_SRC.append(AWS_S3_CUSTOM_DOMAIN)
    CSP_SCRIPT_SRC.append(AWS_S3_CUSTOM_DOMAIN)
    CSP_FONT_SRC.append(AWS_S3_CUSTOM_DOMAIN)
    CSP_IMG_SRC.append(AWS_S3_CUSTOM_DOMAIN)
else:
    # Local storage settings
    STATIC_URL = "/static/"
    STATIC_ROOT = BASE_DIR / "staticfiles"
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "mediafiles"

STATICFILES_DIRS = [BASE_DIR / "static"]

FIXTURE_DIRS = ["test_fixtures"]


# Django REST framework
# https://www.django-rest-framework.org/#installation
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework_xml.parsers.XMLParser",
        "rest_framework_yaml.parsers.YAMLParser",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework_xml.renderers.XMLRenderer",
        "rest_framework_yaml.renderers.YAMLRenderer",
    ),
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "PAGE_SIZE": 10,
}


# drf-spectacular settings
# https://drf-spectacular.readthedocs.io/en/latest/index.html
SPECTACULAR_SETTINGS = {
    "TITLE": "SkillHunter API",
    "DESCRIPTION": """Returns a list of rated skills ordered by number of
    occurrences in vacancies description, including the job title and number of
    vacancies analyzed.""",
    "VERSION": "",
}


# Django Debug Toolbar settings
# https://django-debug-toolbar.readthedocs.io/en/latest/
DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG}


# Production settings
if ENVIRONMENT == "production":
    X_FRAME_OPTIONS = "DENY"
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_REFERRER_POLICY = "same-origin"
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 2592000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NONSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    if "DATABASE_URL" in os.environ:
        DATABASES["default"] = dj_database_url.config(conn_max_age=CONN_MAX_AGE, ssl_require=True)
    # Django error and performance monitoring with Sentry
    if "SENTRY_DSN" in os.environ:
        sentry_sdk.init(  # pylint: disable=abstract-class-instantiated
            dsn=os.getenv("SENTRY_DSN"),
            integrations=[DjangoIntegration(), RedisIntegration()],
            traces_sample_rate=1.0,
            send_default_pii=True,
        )
