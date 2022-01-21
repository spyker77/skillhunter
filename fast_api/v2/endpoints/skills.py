from collections import OrderedDict

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request, status

from scrapers.models import Vacancy

from ..background_tasks import save_query_with_meta_data
from ..schemas import SkillsResponseSchema, VacanciesSchema
from ..utils import sort_skills

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
    limit: int | None = Query(None, description="The number of most wanted skills to display."),
):
    background_tasks.add_task(save_query_with_meta_data, request, q)
    # SearchVector is currently disabled as it does not work properly on AWS RDS due to lack of
    # pg_catalog.english support from the migrations file. Retaled discussions:
    # https://stackoverflow.com/q/40032685/10748367
    # https://forums.aws.amazon.com/thread.jspa?threadID=143920
    # if not (queryset := Vacancy.objects.filter(search_vector=q)):
    if not (queryset := Vacancy.objects.filter(title__search=q)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skills not found")
    serializer = VacanciesSchema.serialize(queryset)
    serialized_data = serializer.dict().get("data")
    sorted_skills = sort_skills(serialized_data)[:limit]
    content = OrderedDict({"vacancy_name": q, "number_of_vacancies": len(queryset), "rated_skills": sorted_skills})
    return content
