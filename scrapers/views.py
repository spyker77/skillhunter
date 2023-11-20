from django.contrib.postgres.search import SearchQuery
from django.views.generic import ListView

from core.tasks import save_query_with_metadata
from core.utils.common import parse_request, sort_skills

from .models import Vacancy

LIMIT_OF_SKILLS = 20


class SearchResultsListView(ListView):
    model = Vacancy
    template_name = "search_results.html"
    context_object_name = "vacancies"

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        search_query = SearchQuery(query)
        return Vacancy.objects.filter(search_vector=search_query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query, limit, user_agent, ip_address = parse_request(self.request)

        save_query_with_metadata.delay(query, user_agent, ip_address)

        queryset = context["vacancies"]
        tailored_skills = sort_skills(queryset)[:LIMIT_OF_SKILLS]

        context.update(
            {
                "vacancy_name": query,
                "number_of_vacancies": queryset.count(),
                "rated_skills": tailored_skills,
            }
        )
        return context
