import asyncio
from django.views.generic import ListView

from .hh_scraper import main


class SearchResultsListView(ListView):
    template_name = "search_results.html"
    context_object_name = "skills_list"

    def get_queryset(self):
        raw_query = self.request.GET.get("q")
        sorted_skills = asyncio.run(main(raw_query))
        skills_list = sorted_skills
        return skills_list
