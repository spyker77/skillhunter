from django.core.cache import cache
from django.core.management.base import BaseCommand

from scrapers.models import Skill, Vacancy


class Command(BaseCommand):
    help = "Keep cache updated with vacancies and skills."

    def handle(self, *args, **options):
        # Ensure that only the necessary fields are loaded.
        skills_cache_key = "skills_from_db"
        vacancies_cache_key = "vacancies"

        # Update skills in cache if they're not already cached.
        if not cache.get(skills_cache_key):
            skills_from_db = Skill.objects.values_list("clean_name", "unclean_names")
            # Convert QuerySet to list to evaluate it before caching.
            cache.set(skills_cache_key, list(skills_from_db), 12 * 60 * 60)

        # Update vacancies in cache if they're not already cached.
        if not cache.get(vacancies_cache_key):
            vacancies = Vacancy.objects.values("url", "title", "rated_skills")
            # Convert QuerySet to list to evaluate it before caching.
            cache.set(vacancies_cache_key, list(vacancies), 12 * 60 * 60)
