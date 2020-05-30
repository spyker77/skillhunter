from django.urls import reverse, resolve

from .views import SearchResultsListView

import pytest


class TestSearchResultsListView:
    @pytest.fixture
    def response(self, client):
        self.url = reverse("search_results")
        test_query = "?q=junior+python+developer"
        return client.get(self.url + test_query)

    def test_searchresultslistview_status_code(self, response):
        assert response.status_code == 200

    def test_searchresultslistview_template(self, response):
        assert "search_results.html" in response.template_name

    def test_searchresultslistview_contains_correct_html(self, response):
        assert "Required skills" in response.rendered_content

    def test_searchresultslistview_does_not_contains_incorrect_html(self, response):
        assert "Hi there! I should not be on the page." not in response.rendered_content

    def test_searchresultslistview_url_resolves_searchresultslistview(self):
        self.view = resolve("/search/")
        assert self.view.func.__name__ == SearchResultsListView.as_view().__name__
