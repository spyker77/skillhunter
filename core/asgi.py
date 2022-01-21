import os

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.wsgi import get_wsgi_application
from fastapi.middleware.wsgi import WSGIMiddleware

try:
    from fast_api.main import create_application
except ImproperlyConfigured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    apps.populate(settings.INSTALLED_APPS)
    from fast_api.main import create_application


# Create main FastAPI application and mount wsgi Django app.
application = create_application()
application.mount("/", WSGIMiddleware(get_wsgi_application()))
