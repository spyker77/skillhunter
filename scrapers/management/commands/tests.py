from unittest.mock import AsyncMock, MagicMock

import pytest
from django.core.management import call_command
from django.db import OperationalError
from django.utils import timezone

from scrapers.models import Vacancy


@pytest.mark.django_db
class TestCleanOutdatedVacancies:
    def test_outdated_vacancies_deleted(self, caplog):
        past_date = timezone.now() - timezone.timedelta(days=8)
        recent_date = timezone.now() - timezone.timedelta(days=1)

        Vacancy.objects.create(
            created_date=past_date,
            rated_skills={"skill_1": 1, "skill_2": 2},
            url="http://unique-url.com/past",
        )
        Vacancy.objects.create(
            created_date=recent_date,
            rated_skills={"skill_1": 1, "skill_2": 2},
            url="http://unique-url.com/recent",
        )

        call_command("purge_db")

        assert Vacancy.objects.filter(created_date=past_date).count() == 0
        assert Vacancy.objects.filter(created_date=recent_date).count() == 1
        assert "Database successfully cleaned from" in caplog.text


@pytest.mark.parametrize(
    "command, scraper_main, site_name, existing_job_url",
    [
        (
            "scrape_hh",
            "scrapers.management.hh_scraper.main",
            "hh.ru",
            "https://hh.ru/existing-job-1",
        ),
        (
            "scrape_indeed",
            "scrapers.management.indeed_scraper.main",
            "indeed.com",
            "https://indeed.com/existing-job-1",
        ),
        (
            "scrape_sh",
            "scrapers.management.sh_scraper.main",
            "simplyhired.com",
            "https://simplyhired.com/existing-job-1",
        ),
    ],
)
@pytest.mark.django_db
class TestScrapeCommand:
    def test_normal_flow_without_errors(self, monkeypatch, command, scraper_main, site_name, existing_job_url, caplog):
        monkeypatch.setattr("scrapers.models.Vacancy.objects.bulk_create", MagicMock())
        mock_main = MagicMock() if "indeed_scraper" in scraper_main else AsyncMock()
        monkeypatch.setattr(scraper_main, mock_main)

        call_command(command)

        assert f"vacancies parsed from {site_name}" in caplog.text

    @pytest.mark.value_error_side_effect
    def test_handling_operational_error(self, monkeypatch, command, scraper_main, site_name, existing_job_url, caplog):
        # Note: This test generates an exception like this in the test results:
        # Exception ignored in: <django.core.management.base.OutputWrapper object at 0x7f3099303d90>
        # Traceback (most recent call last):
        # File "/usr/local/lib/python3.12/site-packages/django/core/management/base.py", line 170, in flush
        #     self._out.flush()
        # ValueError: I/O operation on closed file.
        mock_bulk_create = MagicMock(side_effect=OperationalError("Database error"))
        monkeypatch.setattr("scrapers.models.Vacancy.objects.bulk_create", mock_bulk_create)
        mock_main = MagicMock() if "indeed_scraper" in scraper_main else AsyncMock()
        monkeypatch.setattr(scraper_main, mock_main)

        call_command(command)

        assert "🚨 Got an OperationalError for" in caplog.text
        assert f"💃🕺 {site_name} finished to parse" in caplog.text
