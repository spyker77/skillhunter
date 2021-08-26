from collections import OrderedDict
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request, status

from fast_api.v2.background_tasks import save_query_with_meta_data
from fast_api.v2.schemas import SkillsResponseSchema, VacanciesSchema
from fast_api.v2.utils import sort_skills
from scrapers.models import Vacancy

router = APIRouter()


@router.get(
    "/",
    description="Specify a job title and get the ranked skills that companies expect to see.",
    response_model=SkillsResponseSchema,
)
def show_skills(
    request: Request,
    background_tasks: BackgroundTasks,
    q: str = Query(..., description="The job title to be processed."),
    limit: Optional[int] = Query(None, description="The number of most wanted skills to display."),
):
    background_tasks.add_task(save_query_with_meta_data, request, q)
    if not (queryset := Vacancy.objects.filter(search_vector=q)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skills not found")
    serializer = VacanciesSchema.serialize(queryset)
    serialized_data = serializer.dict().get("data")
    sorted_skills = sort_skills(serialized_data)[:limit]
    content = OrderedDict({"vacancy_name": q, "number_of_vacancies": len(queryset), "rated_skills": sorted_skills})
    return content
