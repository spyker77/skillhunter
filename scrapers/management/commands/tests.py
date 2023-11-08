import pytest
from django.core.management import call_command
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
