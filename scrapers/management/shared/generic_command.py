import logging
import random

from django.core.management.base import BaseCommand
from django.db import OperationalError

from keyword_processor import KeywordProcessor
from scrapers.models import Job, Skill, Vacancy

from .base_scraper import BaseScraper

logger = logging.getLogger("django")


class GenericScrapingCommand(BaseCommand):
    """
    Generic Django management command for scraping job vacancies from various websites.

    This class serves as a base for specific scraping commands. It handles common
    functionalities like fetching job titles, processing skills, and saving the data
    to the database, while delegating the site-specific scraping logic to scraper classes.
    """

    help = "Generic command for scraping job vacancies."

    scraper_class: type[BaseScraper]
    keyword_processor = KeywordProcessor()
    site_name: str

    def handle(self, *args, **options):
        """
        The main method called when the command is run. It orchestrates the scraping process.
        """
        logger.info(f"🚀 {self.site_name} launched to parse!")

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
                existing_links = Vacancy.objects.filter(url__contains=self.site_name).values_list("url", flat=True)

                scraper = self.scraper_class(job_title)
                all_links = scraper.scan_all_search_results()
                new_links = set(all_links) - set(existing_links)
                vacancies_without_skills = scraper.fetch_all_vacancy_pages(new_links)

                self.keyword_processor.add_keywords_from_dict(skills)

                collected_jobs = [
                    scraper.process_vacancy_content(vacancy, self.keyword_processor)
                    for vacancy in vacancies_without_skills
                    if vacancy is not None
                ]

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
                logger.info(f"👍 {job_title} – {number_of_new_vacancies} vacancies parsed from {self.site_name}")

            except OperationalError:
                logger.warning(f"Got an OperationalError for {job_title}.")

        logger.info(f"💃🕺 {self.site_name} finished to parse: {vacancies_parsed} in total!")
