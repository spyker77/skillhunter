from django.core.management.base import BaseCommand
from django.utils import timezone

from scrapers.models import Vacancy


class Command(BaseCommand):
    help = "Clean database from outdated vacancies"

    def handle(self, *args, **options):
        # Delete records older than 7 days.
        past = timezone.datetime.today() - timezone.timedelta(days=7)
        Vacancy.objects.filter(created_date__lte=past).delete()
        self.stdout.write("Database successfully cleaned from outdated records")
