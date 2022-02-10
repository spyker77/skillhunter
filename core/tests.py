from io import StringIO

import pytest
from django.core.management import call_command
from django.test import override_settings
from storages.backends.s3boto3 import S3Boto3Storage

from core import settings
from core.tasks import save_query_with_metadata
from scrapers.models import Search

from .storage_backends import MediaStorage, StaticStorage


class TestSettings:
    def test_settings_production_variables(self):
        assert settings.X_FRAME_OPTIONS
        assert settings.SECURE_BROWSER_XSS_FILTER
        assert settings.SECURE_REFERRER_POLICY
        assert settings.SECURE_SSL_REDIRECT
        assert settings.SECURE_PROXY_SSL_HEADER
        assert settings.SECURE_HSTS_SECONDS
        assert settings.SECURE_HSTS_INCLUDE_SUBDOMAINS
        assert settings.SECURE_HSTS_PRELOAD
        assert settings.SECURE_CONTENT_TYPE_NONSNIFF
        assert settings.SESSION_COOKIE_SECURE
        assert settings.CSRF_COOKIE_SECURE


class TestStorageBackends:
    static_storage_instance = StaticStorage()
    media_storage_instance = MediaStorage()

    def test_static_storage_is_instance_of_s3boto3storage(self):
        assert isinstance(self.static_storage_instance, S3Boto3Storage)

    def test_media_storage_is_instance_of_s3boto3storage(self):
        assert isinstance(self.media_storage_instance, S3Boto3Storage)

    def test_static_storage_has_correct_attributes(self):
        assert self.static_storage_instance.location == "static"
        assert self.static_storage_instance.default_acl == "public-read"

    def test_media_storage_has_correct_attributes(self):
        assert self.media_storage_instance.location == "media"
        assert self.media_storage_instance.default_acl == "public-read"
        assert self.media_storage_instance.file_overwrite is False


@pytest.mark.django_db
class TestPendingMigrations:
    def test_no_pending_migrations(self):
        out = StringIO()
        try:
            call_command("makemigrations", "--dry-run", "--check", stdout=out, stderr=StringIO())
        except SystemExit:  # pragma: no cover
            raise AssertionError("Pending migrations:\n" + out.getvalue()) from None


@pytest.mark.django_db
class TestTasks:
    query = "test search query"
    ip_address = "123.123.123.123"
    user_agent = "Test User-Agent"

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPOGATES=True)
    def test_celery_task_save_query_with_metadata(self):
        result = save_query_with_metadata.delay(self.query, self.user_agent, self.ip_address)
        assert result.successful() is True
        instance = Search.objects.get(ip_address=self.ip_address)
        assert instance.query == self.query
        assert instance.user_agent == self.user_agent
