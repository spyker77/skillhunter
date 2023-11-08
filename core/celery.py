import functools
import os
from threading import RLock

import kombu.utils
from celery import Celery

# This is a workaround for https://github.com/celery/kombu/issues/1804
if not getattr(kombu.utils.cached_property, "lock", None):
    setattr(kombu.utils.cached_property, "lock", functools.cached_property(lambda _: RLock()))
    # Must call __set_name__ here since this cached property is not defined in the context of a class
    # Refer to https://docs.python.org/3/reference/datamodel.html#object.__set_name__
    kombu.utils.cached_property.lock.__set_name__(kombu.utils.cached_property, "lock")
# End of workaround

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
