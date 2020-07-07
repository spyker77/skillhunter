import asyncio
from django.core.management.base import BaseCommand

from .sh_scraper import main
from scrapers.models import Vacancy, Job, Skill


class Command(BaseCommand):
    help = "Scan simplyhired.com and analyze available IT vacancies."

    JOBS = [job.title for job in Job.objects.all()]
    SKILLS = {
        skill.clean_name: eval(skill.unclean_names) for skill in Skill.objects.all()
    }

    def handle(self, *args, **options):
        self.stdout.write(f"🚀 simplyhired.com launched to parse!")
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
            new_vacancies = Vacancy.objects.bulk_create(all_jobs, ignore_conflicts=True)
            self.stdout.write(
                f"👍 {job_title} – {len(new_vacancies)} vacancies parsed from simplyhired.com"
            )
        self.stdout.write(f"💃🕺 simplyhired.com finished to parse!")
