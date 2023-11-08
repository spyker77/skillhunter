from collections.abc import Generator
from operator import itemgetter
from tempfile import SpooledTemporaryFile

import pdftotext
from django.core.cache import cache
from django.core.files.uploadedfile import InMemoryUploadedFile
from flashtext import KeywordProcessor

from scrapers.models import Skill, Vacancy

# # https://stackoverflow.com/a/60458555/10748367
# def convert_to(input_file, output_folder, output_format):
#     # Convert uploaded resume to pdf format using libreoffice.
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
    # Extract text from a PDF resume.
    pdf = pdftotext.PDF(resume_in_memory)
    text_from_resume = "\n\n".join(pdf)
    return text_from_resume


def find_skills_in_resume(text_from_resume: str) -> set[str]:
    # Find unique skills in resume text using the KeywordProcessor for skill extraction.
    skills_from_db = cache.get("skills_from_db")
    if skills_from_db is None:
        skills_from_db = list(Skill.objects.values_list("clean_name", "unclean_names"))
        cache.set("skills_from_db", skills_from_db, 12 * 60 * 60)

    keyword_processor = KeywordProcessor()
    for clean_name, unclean_names in skills_from_db:
        for unclean_name in unclean_names:
            keyword_processor.add_keyword(unclean_name, clean_name)

    skills_from_resume = set(keyword_processor.extract_keywords(text_from_resume))
    return skills_from_resume


def find_suitable_vacancies(skills_in_resume: set[str]) -> Generator[dict[str, str], None, None]:
    # Find vacancies that require the skills from the resume.
    skills_in_resume_lower = {skill.lower() for skill in skills_in_resume}
    # Attempt to retrieve cached vacancies, if not available, query the database and cache them.
    vacancies = cache.get("vacancies")
    if vacancies is None:
        vacancies = list(Vacancy.objects.values("url", "title", "rated_skills"))
        cache.set("vacancies", vacancies, 12 * 60 * 60)

    # Generator expression to filter vacancies based on the presence of resume skills.
    suitable_vacancies = (
        vacancy for vacancy in vacancies if any(skill in skills_in_resume_lower for skill in vacancy["rated_skills"])
    )
    return suitable_vacancies


def sort_suitable_vacancies(
    skills_in_resume: set[str], suitable_vacancies: Generator[dict[str, str], None, None]
) -> list[dict[str, str | int]]:
    # Sort the vacancies by how many skills from the resume match the vacancy's requirements.
    weighted_vacancies = (
        {
            "url": vacancy["url"],
            "title": vacancy["title"],
            "skills_frequency": sum(skill in skills_in_resume for skill in set(vacancy["rated_skills"])),
        }
        for vacancy in suitable_vacancies
    )

    # Sort by the most relevant vacancies and return their titles with links.
    return sorted(weighted_vacancies, key=itemgetter("skills_frequency"), reverse=True)


def analyze_resume(resume_in_memory: SpooledTemporaryFile | InMemoryUploadedFile) -> list[dict[str, str | int]]:
    # Main pipeline function for processing the uploaded resume and finding suitable vacancies.
    text_from_resume = extract_text_from_resume(resume_in_memory)
    skills_in_resume = find_skills_in_resume(text_from_resume)
    suitable_vacancies = find_suitable_vacancies(skills_in_resume)
    tailored_vacancies = sort_suitable_vacancies(skills_in_resume, suitable_vacancies)
    return tailored_vacancies
