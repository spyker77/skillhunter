import os
from collections import defaultdict

from django.views.generic import ListView
from django.contrib.postgres.search import SearchVector

from .models import Vacancy, Search


class SearchResultsListView(ListView):
    model = Vacancy
    template_name = "search_results.html"
    context_object_name = "skills_dict"

    def get_queryset(self):
        query = self.request.GET.get("q")

        # Save the search query for future analysis.
        ENVIRONMENT = os.environ.get("ENVIRONMENT")
        if ENVIRONMENT == "production":
            Search.objects.create(query=query)

        # From here, the main skill collection process continues.
        suitable_vacancies = Vacancy.objects.filter(search_vector=query)
        # Get skills for each vacancy and convert it from str to dict.
        rated_skills_to_merge = (
            eval(vacancy.rated_skills) for vacancy in suitable_vacancies
        )
        # Combine skills from all suitable vacancies into one dict.
        super_dict = defaultdict(list)
        for rated_skills in rated_skills_to_merge:
            if rated_skills != None:
                for k, v in rated_skills.items():
                    super_dict[k].append(v)
            else:
                pass
        # Summ skills that are the same.
        merged_skills = {k: sum(v) for k, v in super_dict.items()}
        # Sort summed skills in descending order and slice TOP-20.
        sorted_skills = sorted(merged_skills.items(), key=lambda x: x[1], reverse=True)[
            :20
        ]
        # Prepare the final result with extra fields for the vacancy name and the number of vacancies found.
        skills_dict = {
            "vacancy_name": query,
            "number_of_vacancies": len(suitable_vacancies),
            "rated_skills": sorted_skills,
        }
        return skills_dict
