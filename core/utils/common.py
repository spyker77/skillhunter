from collections import Counter

from django.db.models.query import QuerySet
from django.utils.html import escape
from rest_framework.request import Request


def parse_request(request: Request) -> tuple[str, int | None, str, str]:
    query = request.GET.get("q")
    if query is not None:
        query = escape(query)

    limit = request.GET.get("limit")
    if limit is not None:
        limit = int(limit)

    user_agent = request.headers.get("User-Agent")
    # Either get the IP address from the HTTP_X_FORWARDED_FOR or from the REMOTE_ADDR header.
    if x_forwarded_for := request.headers.get("X-Forwarded-For"):
        ip_address = x_forwarded_for.split(", ")[0]
    else:
        ip_address = request.META.get("REMOTE_ADDR")

    return query, limit, user_agent, ip_address


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
