import asyncio
from django.core.management.base import BaseCommand

from .hh_scraper import main
from scrapers.models import Vacancy, Job, Skill, Stopword


class Command(BaseCommand):
    help = "Scan job websites and analyze available IT vacancies."

    SKILLS = [skill.name for skill in Skill.objects.all()]
    STOPWORDS = [stopword.name for stopword in Stopword.objects.all()]
    JOBS = [job.title for job in Job.objects.all()]

    def handle(self, *args, **options):
        for job_title in JOBS:
            
            collected_jobs = asyncio.run(main(job_title))
            
            for job in collected_jobs:
                MAKE_THE_WHOLE_PROCESSING
                Vacancy.objects.create(
                        url=job.url,
                        title=job.title,
                        content=job.content
                        rated_skills=job.rated_skills
                    )
