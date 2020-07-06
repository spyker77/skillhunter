import copy
import asyncio
from django.core.management.base import BaseCommand

from .indeed_scraper import main
from scrapers.models import Vacancy, Job, Skill


class Command(BaseCommand):
    help = "Scan indeed.com and analyze available IT vacancies."

    JOBS = [job.title for job in Job.objects.all()]
    SKILLS = {
        skill.clean_name: eval(skill.unclean_names) for skill in Skill.objects.all()
    }

    def handle(self, *args, **options):
        self.stdout.write(f"🚀 indeed.com launched to parse!")
        for job_title in self.JOBS:
            collected_jobs = asyncio.run(main(job_title, self.SKILLS))
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
            copied_all_jobs = copy.copy(list(all_jobs))
            Vacancy.objects.bulk_create(all_jobs, ignore_conflicts=True)
            self.stdout.write(
                f"👍 {job_title} – {len(copied_all_jobs)} vacancies parsed from indeed.com"
            )
        self.stdout.write(f"💃🕺 indeed.com finished to parse!")
