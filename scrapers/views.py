import os
from collections import defaultdict

from django.views.generic import ListView

from .models import Vacancy, Search


class SearchResultsListView(ListView):
    model = Vacancy
    template_name = "search_results.html"
    context_object_name = "skills_dict"

    def _combine_rated_skills(self, rated_skills_to_merge):
        super_dict = defaultdict(list)
        for rated_skills in rated_skills_to_merge:
            if rated_skills != None:
                for k, v in rated_skills.items():
                    super_dict[k].append(v)
        return super_dict

    def get_queryset(self):
        query = self.request.GET.get("q")
        ip_address = self.request.META.get("REMOTE_ADDR")
        user_agent = self.request.META.get("HTTP_USER_AGENT")

        # Save the search query for future analysis.
        ENVIRONMENT = os.environ.get("ENVIRONMENT")
        if ENVIRONMENT == "production":
            Search.objects.create(
                query=query, ip_address=ip_address, user_agent=user_agent
            )

        # From here, the main skill collection process continues.
        suitable_vacancies = Vacancy.objects.filter(search_vector=query)
        # Get skills for each vacancy and convert it from str to dict.
        rated_skills_to_merge = (
            eval(vacancy.rated_skills) for vacancy in suitable_vacancies
        )
        # Combine skills from all suitable vacancies into one dict.
        super_dict = self._combine_rated_skills(rated_skills_to_merge)
        # Summ skills that are the same.
        merged_skills = {k: sum(v) for k, v in super_dict.items()}
        # Sort summed skills in descending order and slice TOP-20.
        sorted_skills = sorted(merged_skills.items(), key=lambda x: x[1], reverse=True)[
            :20
        ]
        # Prepare the final result with extra fields for the vacancy name and
        # the number of vacancies found.
        skills_dict = {
            "vacancy_name": query,
            "number_of_vacancies": len(suitable_vacancies),
            "rated_skills": sorted_skills,
        }
        return skills_dict
