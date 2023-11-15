import logging
import random

from django.core.management.base import BaseCommand
from django.db import OperationalError

from scrapers.management.indeed_scraper import main
from scrapers.models import Job, Skill, Vacancy

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "Scan indeed.com and analyze available IT vacancies."

    def handle(self, *args, **options):
        logger.info("🚀 indeed.com launched to parse!")

        jobs = list(Job.objects.values_list("title", flat=True))
        skills = {
            skill["clean_name"]: skill["unclean_names"]
            for skill in Skill.objects.values("clean_name", "unclean_names")
        }

        # Shuffle the list of jobs each time to prevent timeout errors for
        # the same jobs and subsequent constant data loss.
        random.shuffle(jobs)
        vacancies_parsed = 0

        for job_title in jobs:
            try:
                indeed_links_we_already_have = set(
                    Vacancy.objects.filter(url__contains="indeed.com").values_list("url", flat=True)
                )
                collected_jobs = main(job_title, indeed_links_we_already_have, skills)
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
                logger.info(f"👍 {job_title} – {number_of_new_vacancies} vacancies parsed from indeed.com")
            except OperationalError:
                logger.warning(f"Got an OperationalError for {job_title}.")

        logger.info(f"💃🕺 indeed.com finished to parse: {vacancies_parsed} in total!")
