from django.urls import reverse, resolve

from .views import SearchResultsListView
from .models import Search

import pytest


@pytest.mark.django_db
class TestSearchResultsListView:
    url = reverse("search_results")
    data = {"q": "test search query"}
    query = data.get("q")
    ip_address = "0.0.0.0"
    user_agent = "Test User-Agent"

    @pytest.fixture
    def mock_environment_production(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")

    @pytest.fixture
    def response(self, monkeypatch, rf):
        request = rf.get(
            self.url,
            self.data,
            REMOTE_ADDR=self.ip_address,
            HTTP_USER_AGENT=self.user_agent,
        )
        return SearchResultsListView.as_view()(request)

    def test_searchresultslistview_status_code(self, response):
        assert response.status_code == 200

    def test_searchresultslistview_template(self, response):
        assert "search_results.html" in response.template_name

    def test_searchresultslistview_contains_correct_html(self, response):
        assert "Skills you need to be a" in response.rendered_content

    def test_searchresultslistview_does_not_contain_incorrect_html(self, response):
        assert "Hi there! I should not be on the page." not in response.rendered_content

    def test_searchresultslistview_url_resolves_searchresultslistview(self):
        view = resolve("/search/")
        assert view.func.__name__ == SearchResultsListView.as_view().__name__

    def test_searchresultslistview_creates_new_search_object(
        self, mock_environment_production, response
    ):
        new_search_object = Search.objects.filter(user_agent=self.user_agent)
        assert new_search_object[0].query == self.query
        assert new_search_object[0].ip_address == self.ip_address
        assert new_search_object[0].user_agent == self.user_agent

    def test_searchresultslistview_combines_rated_skills(self):
        rated_skills_to_merge = (
            {"Python": 1, "JS": 2},
            {"Python": 3, "AWS": 1},
            None,
        )
        super_dict = SearchResultsListView._combine_rated_skills(
            self, rated_skills_to_merge
        )
        merged_skills = {k: sum(v) for k, v in super_dict.items()}
        assert merged_skills["Python"] == 4
        assert None not in merged_skills
