from django.core.cache import cache
from django.core.management.base import BaseCommand

from scrapers.models import Skill, Vacancy


class Command(BaseCommand):
    help = "Keep cache updated with vacancies and skills."

    def handle(self, *args, **options):
        skills_from_db = cache.get("skills_from_db")
        # Cache skills for 12 hours.
        if skills_from_db is None:
            skills_from_db = list(Skill.objects.all())
            cache.set("skills_from_db", skills_from_db, 12 * 60 * 60)
        vacancies = cache.get("vacancies")
        # Cache vacancies for 12 hours.
        if vacancies is None:
            vacancies = list(Vacancy.objects.values("url", "title", "rated_skills"))
            cache.set("vacancies", vacancies, 12 * 60 * 60)
