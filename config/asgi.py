import os

from django.apps import apps
from django.conf import settings
from django.core.asgi import get_asgi_application
from django.core.exceptions import ImproperlyConfigured

try:
    from fast_api.main import create_application
except ImproperlyConfigured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    apps.populate(settings.INSTALLED_APPS)
    from fast_api.main import create_application


# Create main FastAPI application and mount Django app
application = create_application()
application.mount("/", get_asgi_application())
