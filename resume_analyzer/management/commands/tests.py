import pytest
from django.core.cache import cache
from django.core.management import call_command


@pytest.mark.django_db
class TestWarmupCache:
    def test_successful_cache_warmup(self):
        cache.clear()
        # Make sure the initial cache is clean.
        skills_from_db = cache.get("skills_from_db")
        vacancies = cache.get("vacancies")
        assert skills_from_db is None
        assert vacancies is None
        call_command("warmup_cache")
        # Check that cache is updated.
        skills_from_db = cache.get("skills_from_db")
        vacancies = cache.get("vacancies")
        assert skills_from_db is not None
        assert vacancies is not None
