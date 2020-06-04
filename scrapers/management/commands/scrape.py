import re
import asyncio
from django.core.management.base import BaseCommand

from .hh_scraper import main
from scrapers.models import Vacancy, Job, Skill, Stopword


class Command(BaseCommand):
    help = "Scan job websites and analyze available IT vacancies."

    SKILLS = [skill.name for skill in Skill.objects.all()]
    STOPWORDS = [stopword.name for stopword in Stopword.objects.all()]
    JOBS = (job.title for job in Job.objects.all())

    def process_vacancy_content(self, vacancy_without_skills):
        # Extract keywords from the content of the vacancy and count each keyword.
        content = vacancy_without_skills["content"]
        counts = dict()
        # This pattern doesn't identify phrases like "Visual Basic .NET"!
        pattern = r"\w+\S+\w+|[a-zA-Z]+[+|#]+|\S+[a-zA-Z]|\w+"
        if content != None:
            separated_words = re.findall(pattern, content.casefold())
            # Clean from the unnecessary stopwords.
            cleaned_words = (
                word for word in separated_words if word not in self.STOPWORDS
            )
            for word in cleaned_words:
                case_insensitive_counts = (key.casefold() for key in counts)
                case_insensitive_skills = [
                    element.casefold() for element in self.SKILLS
                ]

                # Rate skills by frequency.
                if word in case_insensitive_counts and word in case_insensitive_skills:
                    position = case_insensitive_skills.index(word)
                    counts[self.SKILLS[position]] += 1
                elif (
                    word not in case_insensitive_counts
                    and word in case_insensitive_skills
                ):
                    position = case_insensitive_skills.index(word)
                    counts[self.SKILLS[position]] = 1
                else:
                    pass
            skills = {"rated_skills": counts}
            vacancy_plus_skills = vacancy_without_skills.copy()
            vacancy_plus_skills.update(skills)
            return vacancy_plus_skills
        else:
            pass

    def handle(self, *args, **options):
        for job_title in self.JOBS:
            vacancies_without_skills = asyncio.run(main(job_title))
            collected_jobs = (
                self.process_vacancy_content(vacancy_without_skills)
                for vacancy_without_skills in vacancies_without_skills
            )
            all_jobs = (
                Vacancy(
                    url=job["url"],
                    title=job["title"],
                    content=job["content"],
                    rated_skills=job["rated_skills"],
                )
                for job in collected_jobs
            )
            Vacancy.objects.bulk_create(all_jobs, ignore_conflicts=True)
            self.stdout.write(f"👍 {job_title} 👍 – parsed and added to DB.")
