import ast
import json
from collections.abc import Generator
from tempfile import SpooledTemporaryFile

import pdftotext
from django.core.cache import cache
from django.core.files.uploadedfile import InMemoryUploadedFile
from flashtext import KeywordProcessor

from scrapers.models import Skill, Vacancy

# https://stackoverflow.com/a/60458555/10748367
# def convert_to(input_file, output_folder, output_format):
# # Convert uploaded resume to pdf format using libreoffice.
#     args = [
#         "soffice",
#         "--headless",
#         "--convert-to",
#         output_format,
#         "--outdir",
#         output_folder,
#         input_file,
#     ]
#     process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     filename = re.search("-> (.*?) using filter", process.stdout.decode())
#     return filename.group(1)


def extract_text_from_resume(resume_in_memory: SpooledTemporaryFile | InMemoryUploadedFile) -> str:
    # Extract text from the pdf resume file.
    pdf = pdftotext.PDF(resume_in_memory)
    text_from_resume = "\n\n".join(pdf)
    return text_from_resume


def find_skills_in_resume(text_from_resume: str) -> set[str]:
    # Extract from resume the list of unique skills that need to be matched against the vacancies.
    skills_from_db = cache.get("skills_from_db")
    # Cache skills for 12 hours – additional check despite the custom cron command to warmup the cache.
    if skills_from_db is None:
        skills_from_db = list(Skill.objects.all())
        cache.set("skills_from_db", skills_from_db, 12 * 60 * 60)
    skills = {skill.clean_name: ast.literal_eval(skill.unclean_names) for skill in skills_from_db}
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keywords_from_dict(skills)
    skills_from_resume = set(keyword_processor.extract_keywords(text_from_resume))
    return skills_from_resume


def find_suitable_vacancies(skills_in_resume: set[str]) -> Generator[dict[str, str], None, None]:
    # Find vacancies that require the skills from resume.
    vacancies = cache.get("vacancies")
    # Cache vacancies for 12 hours – additional check despite the custom cron command to warmup the cache.
    if vacancies is None:
        vacancies = list(Vacancy.objects.values("url", "title", "rated_skills"))
        cache.set("vacancies", vacancies, 12 * 60 * 60)
    suitable_vacancies = (
        vacancy
        for vacancy in vacancies
        for skill in skills_in_resume
        if skill.lower() in vacancy["rated_skills"].lower()
    )
    return suitable_vacancies


def sort_suitable_vacancies(
    skills_in_resume: set[str], suitable_vacancies: Generator[dict[str, str], None, None]
) -> list[tuple[str, tuple[str, int]]]:
    # Find how many skills from resume are present in rated skills of vacancies and sort the result.
    weighted_vacancies: dict = {}
    for vacancy in suitable_vacancies:
        rated_skills = json.loads(vacancy["rated_skills"])
        # Use 1 to avoid spam in vacancy description and count each unique skill just once.
        intersected_skills = {skill: 1 for skill in rated_skills.keys() if skill in skills_in_resume}
        total_of_intersected_skills = sum(intersected_skills.values())
        weighted_vacancies.update({vacancy["url"]: (vacancy["title"], total_of_intersected_skills)})
    # Additional validation to avoid duplicate vacancies – a tricky way due to optimization.
    reverted_dict: dict = {}
    for key, value in weighted_vacancies.items():
        reverted_dict.setdefault(value, set()).add(key)
    unique_vacancies = {list(value)[0]: key for key, value in reverted_dict.items()}
    # Sort by the most relevant vacancies and return their titles with links.
    tailored_vacancies = sorted(unique_vacancies.items(), key=lambda x: x[1][1], reverse=True)
    return tailored_vacancies


def put_tailored_vacancies_in_dicts(
    tailored_vacancies: list[tuple[str, tuple[str, int]]]
) -> list[dict[str, str | int]]:
    # Put the tailored vacancies in dicts for easier access.
    dicted_tailored_vacancies = [
        {
            "url": vacancy[0],
            "title": vacancy[1][0],
            "skills_frequency": vacancy[1][1],
        }
        for vacancy in tailored_vacancies
    ]
    return dicted_tailored_vacancies


def analyze_resume(
    resume_in_memory: SpooledTemporaryFile | InMemoryUploadedFile,
) -> list[dict[str, str | int]]:
    # Main pipeline for processing the uploaded resume.
    text_from_resume = extract_text_from_resume(resume_in_memory)
    skills_in_resume = find_skills_in_resume(text_from_resume)
    suitable_vacancies = find_suitable_vacancies(skills_in_resume)
    tailored_vacancies = sort_suitable_vacancies(skills_in_resume, suitable_vacancies)
    dicted_tailored_vacancies = put_tailored_vacancies_in_dicts(tailored_vacancies)
    return dicted_tailored_vacancies
