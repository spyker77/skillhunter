import json
from collections import defaultdict
from typing import DefaultDict, Dict, Generator, List, Tuple


def _combine_rated_skills(rated_skills_to_merge: Generator[Dict[str, int], None, None]) -> DefaultDict[str, List[int]]:
    # Combine skills from all suitable vacancies into one dict.
    super_dict = defaultdict(list)
    for rated_skills in rated_skills_to_merge:
        if rated_skills is not None:
            for k, v in rated_skills.items():
                super_dict[k].append(v)
    return super_dict


def sort_skills(serialized_data: List) -> List[Tuple[str, int]]:
    # Get rated skills for each vacancy and convert it from str to dict.
    rated_skills_to_merge = (json.loads(vacancy.get("rated_skills")) for vacancy in serialized_data)
    super_dict = _combine_rated_skills(rated_skills_to_merge)
    # Summ skills that are the same.
    merged_skills = {k: sum(v) for k, v in super_dict.items()}
    # Sort summed skills in descending order.
    sorted_skills = sorted(merged_skills.items(), key=lambda x: x[1], reverse=True)
    return sorted_skills
