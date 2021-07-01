from collections import OrderedDict
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from fast_api.v2.schemas import SkillsResponseSchema, VacanciesSchema
from fast_api.v2.utils import sort_skills
from scrapers.models import Vacancy

router = APIRouter()


@router.get("/", response_model=SkillsResponseSchema)
def show_skills(
    q: str = Query(..., description="The job title to be processed."),
    limit: Optional[int] = Query(None, description="The number of most wanted skills to display."),
):
    queryset = Vacancy.objects.filter(search_vector=q)
    if not queryset:
        raise HTTPException(status_code=404, detail="Skills not found")
    serializer = VacanciesSchema.serialize(queryset)
    serialized_data = serializer.dict().get("data")
    sorted_skills = sort_skills(serialized_data)
    if limit:
        sorted_skills = sorted_skills[: int(limit)]
    content = OrderedDict({"vacancy_name": q, "number_of_vacancies": len(queryset), "rated_skills": sorted_skills})
    return content
