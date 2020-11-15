from django.urls import path
from django.views.decorators.cache import cache_page

from .views import SearchResultsListView

CACHE_SECONDS = 12 * 60 * 60

urlpatterns = [
    path(
        "",
        cache_page(CACHE_SECONDS)(SearchResultsListView.as_view()),
        name="search_results",
    ),
]
