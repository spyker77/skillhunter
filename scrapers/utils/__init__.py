import json
from collections import defaultdict
from collections.abc import Generator
from typing import DefaultDict


def _combine_rated_skills(rated_skills_to_merge: Generator[dict[str, int], None, None]) -> DefaultDict[str, list[int]]:
    # Combine skills from all suitable vacancies into one dict.
    super_dict = defaultdict(list)
    for rated_skills in rated_skills_to_merge:
        if rated_skills is not None:
            for k, v in rated_skills.items():
                super_dict[k].append(v)
    return super_dict


def _put_sorted_skills_in_dicts(sorted_skills: list[tuple[str, int]]) -> list[dict[str, int]]:
    # Put the sorted skills into dicts for easier access.
    dicted_skills = [{"skill": skill[0], "frequency": skill[1]} for skill in sorted_skills]
    return dicted_skills


def sort_skills(vacancies: list) -> list[tuple[str, int]]:
    # Get rated skills for each vacancy and convert it from str to dict.
    rated_skills_to_merge = (json.loads(vacancy.rated_skills) for vacancy in vacancies)
    super_dict = _combine_rated_skills(rated_skills_to_merge)
    # Summ skills that are the same.
    merged_skills = {k: sum(v) for k, v in super_dict.items()}
    # Sort summed skills in descending order.
    sorted_skills = sorted(merged_skills.items(), key=lambda x: x[1], reverse=True)
    tailored_skills = _put_sorted_skills_in_dicts(sorted_skills)
    return tailored_skills
