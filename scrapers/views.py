import collections

from django.db.models import Q
from django.views.generic import ListView

from .models import Vacancy


class SearchResultsListView(ListView):
    model = Vacancy
    template_name = "search_results.html"
    context_object_name = "skills_dict"

    def get_queryset(self):
        query = self.request.GET.get("q")
        suitable_vacancies = Vacancy.objects.filter(
            Q(title__icontains=query) & Q(content__icontains=query)
        )
        # Get skills for each vacancy and convert it from str to dict.
        rated_skills_to_merge = (
            eval(vacancy.rated_skills) for vacancy in suitable_vacancies
        )
        # Combine skills from all suitable vacancies into one dict.
        super_dict = collections.defaultdict(list)
        for rated_skills in rated_skills_to_merge:
            if rated_skills != None:
                for k, v in rated_skills.items():
                    super_dict[k].append(v)
            else:
                pass
        merged_skills = {k: sum(v) for k, v in super_dict.items()}
        # Prepare the final result with extra fields for vacancy name and its quantity.
        skills_dict = {
            "vacancy_name": query,
            "number_of_vacancies": len(suitable_vacancies),
            "skills": merged_skills,
        }
        return skills_dict
