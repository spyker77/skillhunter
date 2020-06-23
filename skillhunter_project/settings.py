import os
import socket

import django_heroku
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENVIRONMENT = os.environ.get("ENVIRONMENT", default="production")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", default=0))

ALLOWED_HOSTS = [
    "skillhunter.app",
    "skillhunter-app.herokuapp.com",
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
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "scrapers",
    "pages",
    "crispy_forms",
    "debug_toolbar",
    "robots",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "skillhunter_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [os.path.join(BASE_DIR, "templates/jinja2")],
        "APP_DIRS": True,
        "OPTIONS": {"environment": "skillhunter_project.jinja2.environment",},
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "skillhunter_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DATABASE_NAME"),
        "USER": os.environ.get("DATABASE_USER"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
        "HOST": "localhost",
        "PORT": "",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


CRISPY_TEMPLATE_PACK = "bootstrap4"


# Content-Security-Policy settings for django-csp
CSP_DEFAULT_SRC = [
    "'self'",
    "front.optimonk.com",
]
CSP_STYLE_SRC = [
    "'self'",
]
CSP_SCRIPT_SRC = [
    "'self'",
    "'unsafe-inline'",
    "front.optimonk.com",
]
CSP_FONT_SRC = [
    "'self'",
]
CSP_IMG_SRC = [
    "'self'",
]


# django-debug-toolbar
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + "1" for ip in ips]
# if DEBUG:
#     DEBUG_TOOLBAR_CONFIG = {
#         "SHOW_TOOLBAR_CALLBACK": lambda request: not request.is_ajax()
#     }
#     CSP_SCRIPT_SRC.append("'unsafe-inline'")
#     CSP_STYLE_SRC.append("'unsafe-inline'")


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
    DATABASES["default"] = dj_database_url.config(conn_max_age=600, ssl_require=True)


# # Memcachier for Heroku
servers = os.environ.get("MEMCACHIER_SERVERS")
username = os.environ.get("MEMCACHIER_USERNAME")
password = os.environ.get("MEMCACHIER_PASSWORD")

CACHES = {
    "default": {
        # Use django-bmemcached
        "BACKEND": "django_bmemcached.memcached.BMemcached",
        # TIMEOUT is not the connection timeout! It's the default expiration
        # timeout that should be applied to keys! Setting it to `None`
        # disables expiration.
        "TIMEOUT": 12 * 60 * 60,
        "LOCATION": servers,
        "OPTIONS": {"username": username, "password": password,},
    }
}

# Cashing
CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_SECONDS = 12 * 60 * 60
CACHE_MIDDLEWARE_KEY_PREFIX = ""


django_heroku.settings(locals())
