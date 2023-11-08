from collections import Counter

from django.db.models.query import QuerySet


def sort_skills(vacancies: QuerySet | list[dict[str, int]]) -> list[dict[str, int]]:
    # Combine skills from all suitable vacancies and sum their frequencies.
    skills_counter = Counter()
    for vacancy in vacancies:
        skills_counter.update(vacancy.rated_skills)

    # Sort summed skills in descending order and create a list of dicts.
    sorted_skills_dicts = [
        {"skill": skill, "frequency": frequency} for skill, frequency in skills_counter.most_common()
    ]

    return sorted_skills_dicts
