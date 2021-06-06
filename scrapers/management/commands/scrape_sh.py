import ast
import asyncio
import logging.config
import random

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import OperationalError

from scrapers.management.commands.sh_scraper import main
from scrapers.models import Job, Skill, Vacancy

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger()


class Command(BaseCommand):
    help = "Scan simplyhired.com and analyze available IT vacancies."

    jobs = [job.title for job in Job.objects.all()]
    skills = {skill.clean_name: ast.literal_eval(skill.unclean_names) for skill in Skill.objects.all()}

    def handle(self, *args, **options):
        logger.info("🚀 simplyhired.com launched to parse!")
        # Shuffle the list of jobs each time to prevent timeout errors for
        # the same jobs and subsequent constant data loss.
        random.shuffle(self.jobs)
        vacancies_parsed = 0
        for job_title in self.jobs:
            try:
                sh_links_we_already_have = [
                    url
                    for url in Vacancy.objects.filter(url__contains="simplyhired.com").values_list("url", flat=True)
                ]
                collected_jobs = asyncio.run(main(job_title, sh_links_we_already_have, self.skills))
                all_jobs = (
                    Vacancy(
                        url=job["url"],
                        title=job["title"],
                        content=job["content"],
                        rated_skills=job["rated_skills"],
                    )
                    for job in collected_jobs
                    if job is not None
                )
                new_vacancies = Vacancy.objects.bulk_create(all_jobs)
                number_of_new_vacancies = len(new_vacancies)
                vacancies_parsed += number_of_new_vacancies
                logger.ingo(f"👍 {job_title} – {number_of_new_vacancies} vacancies parsed from simplyhired.com")
            except OperationalError:
                logger.warning(f"🚨 Got an OperationalError for {job_title}.")
        logger.info(f"💃🕺 simplyhired.com finished to parse: {vacancies_parsed} in total!")
