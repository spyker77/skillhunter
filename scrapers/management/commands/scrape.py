import asyncio
from django.core.management.base import BaseCommand

from .skillhunter_v3 import main


class Command(BaseCommand):
    help = "Find out required skills for the job"

    def handle(self, *args, **options):
        asyncio.run(main())
