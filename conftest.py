from django.conf import settings

import pytest


@pytest.fixture(scope="session")
def django_db_setup():
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "db.example.com",
        "NAME": "external_db",
    }
