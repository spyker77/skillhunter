from django.urls import path

from .views import SearchResultsListView

urlpatterns = [
    path("", SearchResultsListView.as_view(), name="search-results"),
]
