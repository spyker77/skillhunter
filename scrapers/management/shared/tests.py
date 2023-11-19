from unittest.mock import Mock, create_autospec

import pytest
from django.core.management import call_command
from django.db import OperationalError
from django.utils import timezone
from playwright.sync_api import Error, Page

from scrapers.models import Vacancy

from .base_scraper import BaseScraper
from .utils import get_playwright_page, get_user_agent


def test_get_playwright_page():
    with get_playwright_page() as page:
        assert isinstance(page, Page)

    # After the context manager exits, the page should be closed.
    with pytest.raises(Error):
        _ = page.title()


@pytest.mark.parametrize(
    "os_name, expected_agent",
    [("darwin", "Mac"), ("windows", "Windows"), ("linux", "Linux")],
)
def test_get_user_agent(monkeypatch, os_name, expected_agent):
    monkeypatch.setattr("platform.system", lambda: os_name)
    user_agent = get_user_agent()
    assert expected_agent in user_agent


@pytest.mark.django_db
def test_purge_db_command(caplog):
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
    "site_name, command_name, scraper_path",
    [
        ("hh.ru", "scrape_hh", "scrapers.management.hh_scraper.HHScraper"),
        ("indeed.com", "scrape_indeed", "scrapers.management.indeed_scraper.IndeedScraper"),
        ("simplyhired.com", "scrape_sh", "scrapers.management.sh_scraper.SHScraper"),
    ],
)
@pytest.mark.django_db
class TestScrapingCommands:
    @pytest.fixture
    def mock_scraper(self):
        mock = create_autospec(BaseScraper, instance=True)
        mock.scan_all_search_results.return_value = {"link_1", "link_2"}
        mock.fetch_all_vacancy_pages.return_value = [{"url": "link_1", "title": "Job 1", "content": "Content 1"}]
        mock.process_vacancy_content.return_value = {
            "url": "link_1",
            "title": "Job 1",
            "content": "Content 1",
            "rated_skills": {"Skill 1": 1, "Skill 2": 2},
        }
        return mock

    def test_handle_normal_operation(self, monkeypatch, site_name, command_name, scraper_path, mock_scraper, caplog):
        monkeypatch.setattr("scrapers.models.Job.objects.values_list", Mock(return_value=["Developer", "Designer"]))
        monkeypatch.setattr("scrapers.models.Vacancy.objects.bulk_create", Mock(return_value=[]))
        monkeypatch.setattr(scraper_path, Mock(return_value=mock_scraper))

        call_command(command_name)

        assert f"vacancies parsed from {site_name}" in caplog.text

    def test_handle_with_operational_error(
        self, monkeypatch, site_name, command_name, scraper_path, mock_scraper, caplog
    ):
        monkeypatch.setattr("scrapers.models.Job.objects.values_list", Mock(return_value=["Developer", "Designer"]))
        monkeypatch.setattr("scrapers.models.Vacancy.objects.bulk_create", Mock(side_effect=OperationalError))
        monkeypatch.setattr(scraper_path, Mock(return_value=mock_scraper))

        call_command(command_name)

        assert "Got an OperationalError for" in caplog.text
        assert f"💃🕺 {site_name} finished to parse" in caplog.text
