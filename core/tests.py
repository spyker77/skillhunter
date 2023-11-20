import time
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from unittest.mock import patch

import pytest
from celery.exceptions import Retry
from django.conf import settings
from django.core.management import call_command
from django.test import override_settings
from storages.backends.s3boto3 import S3Boto3Storage

from scrapers.models import Search

from .storage_backends import MediaStorage, StaticStorage
from .tasks import save_query_with_metadata
from .utils.celery import lock_task


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

    @pytest.fixture(autouse=True)
    def setup_tests(self):
        with override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPOGATES=True):
            yield

    def test_celery_task_save_query_with_metadata_success(self):
        result = save_query_with_metadata.delay(self.query, self.user_agent, self.ip_address)
        assert result.successful()
        assert Search.objects.filter(ip_address=self.ip_address).exists()

    @patch("core.tasks.save_query_with_metadata.retry", side_effect=Retry())
    @patch("scrapers.models.Search.objects.create")
    def test_celery_task_save_query_with_metadata_retry(self, mock_create, mock_retry):
        mock_create.side_effect = [Exception("Transient Error"), None]
        save_query_with_metadata.delay(self.query, self.user_agent, self.ip_address)
        assert mock_retry.call_count == 1
        assert mock_create.call_count >= 1  # At least once before the `retry_backoff` kicks in.

    @patch("core.tasks.save_query_with_metadata.retry", side_effect=Retry())
    @patch("scrapers.models.Search.objects.create", side_effect=Exception("Persistent Error"))
    def test_celery_task_save_query_with_metadata_logging(self, mock_create, mock_retry, caplog):
        save_query_with_metadata.delay(self.query, self.user_agent, self.ip_address)
        assert "Error saving search query." in caplog.text


class TestLockTaskDecorator:
    def mock_task(self, key, raise_exception=False, sleep_time=2):
        @lock_task(key, timeout=10)
        def task():
            # Simulate task execution time and handle exceptions.
            try:
                time.sleep(sleep_time)
                if raise_exception:
                    raise Exception("Simulated Task Failure")
                return "Executed"
            except Exception as e:
                return str(e)

        return task

    def test_lock_acquisition_exception(self):
        task = self.mock_task("test_lock_acquisition")
        with patch("core.utils.celery.redis_client.lock") as mock_lock:
            mock_lock.return_value.acquire.side_effect = Exception("Lock acquisition failed")
            task()
        assert mock_lock.call_count == 1

    def test_lock_release_after_exception(self):
        task_with_exception = self.mock_task("test_lock_release", raise_exception=True)
        assert task_with_exception() == "Simulated Task Failure"
        task = self.mock_task("test_lock_release", raise_exception=False)
        assert task() == "Executed"

    def test_concurrent_execution_with_lock(self):
        task = self.mock_task("test_concurrent_execution")
        with ThreadPoolExecutor(max_workers=2) as executor:
            first_task = executor.submit(task)
            time.sleep(0.2)
            second_task = executor.submit(task, raise_exception=True)

            first_result = first_task.result()
            second_result = second_task.result()

            # Validate that one task executed successfully and the other raised an exception.
            assert (first_result == "Executed") != (second_result == "Simulated Task Failure")
