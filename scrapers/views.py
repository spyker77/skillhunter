from django.views.generic import ListView

from core.tasks import save_query_with_metadata
from core.utils import parse_request

from .models import Vacancy
from .utils import sort_skills

LIMIT_OF_SKILLS = 20


class SearchResultsListView(ListView):
    model = Vacancy
    template_name = "search_results.html"
    context_object_name = "skills_dict"

    def get_queryset(self):
        query, limit, user_agent, ip_address = parse_request(self.request)
        save_query_with_metadata.delay(query, user_agent, ip_address)

        # SearchVector is currently disabled as it does not work properly on AWS RDS due to lack of
        # pg_catalog.english support from the migrations file. Retaled discussions:
        # https://stackoverflow.com/q/40032685/10748367
        # https://forums.aws.amazon.com/thread.jspa?threadID=143920
        # queryset = Vacancy.objects.filter(search_vector=query)

        queryset = Vacancy.objects.filter(title__search=query)
        tailored_skills = sort_skills(queryset)[:LIMIT_OF_SKILLS]
        skills_dict = {
            "vacancy_name": query,
            "number_of_vacancies": len(queryset),
            "rated_skills": tailored_skills,
        }
        return skills_dict
