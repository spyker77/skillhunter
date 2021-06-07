import logging
import logging.config

from django.core.management.base import BaseCommand
from django.utils import timezone

from scrapers.management.logging_config import LOGGING
from scrapers.models import Vacancy

logging.config.dictConfig(LOGGING)
logger = logging.getLogger()


class Command(BaseCommand):
    help = "Clean database from outdated vacancies."

    def handle(self, *args, **options):
        # Delete records older than 7 days (before scraping new data).
        past = timezone.now() - timezone.timedelta(days=7)
        outdated_vacancies = Vacancy.objects.filter(created_date__lte=past)
        amount = outdated_vacancies.count()
        outdated_vacancies.delete()
        logger.info(f"🗂️ Database successfully cleaned from {amount} outdated vacancies.")
