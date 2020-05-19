import asyncio
from django.views.generic import ListView

from .scraper import main


class SearchResultsListView(ListView):
    template_name = "search_results.html"
    context_object_name = "skills_list"

    def get_queryset(self):
        raw_query = self.request.GET.get("q")
        sorted_counts = asyncio.run(main(raw_query))
        skills_list = sorted_counts
        return skills_list
