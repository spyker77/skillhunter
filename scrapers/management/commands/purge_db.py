from django.core.management.base import BaseCommand
from django.utils import timezone

from scrapers.models import Vacancy


class Command(BaseCommand):
    help = "Clean database from outdated vacancies."

    def handle(self, *args, **options):
        # Delete records older than 7 days (before scraping new data).
        past = timezone.now() - timezone.timedelta(days=7)
        outdated_vacancies = Vacancy.objects.filter(created_date__lte=past)
        amount = outdated_vacancies.count()
        outdated_vacancies.delete()
        self.stdout.write(f"🗂️ Database successfully cleaned from {amount} outdated vacancies.")
