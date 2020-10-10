from pathlib import Path
from urllib.parse import urlparse, urlencode

from django.urls import reverse, resolve

from .apps import ScrapersConfig
from .views import SearchResultsListView
from .models import Vacancy, Job, Search, Skill

import pytest


@pytest.mark.django_db
class TestSearchResultsListView:
    url = reverse("search_results")
    data = {"q": "test search query"}
    query = data.get("q")
    ip_address = "9.9.9.9"
    user_agent = "Test User-Agent"

    @pytest.fixture
    def response(self, client):
        response = client.get(
            self.url,
            self.data,
            follow=True,
            REMOTE_ADDR=self.ip_address,
            HTTP_USER_AGENT=self.user_agent,
        )
        return response

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

    def test_searchresultslistview_creates_new_search_object(self, response):
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


@pytest.mark.django_db
class TestVacancyModel:
    def test_vacancymodel_str_method(self):
        Vacancy.objects.create(
            url="http://test_url.app",
            title="Test vacancy",
            content="Test content",
            rated_skills={"Python": 1, "JS": 2},
        )
        vacancy_object = Vacancy.objects.get(url="http://test_url.app")
        assert str(vacancy_object) == vacancy_object.title


@pytest.mark.django_db
class TestJobModel:
    title = "Test job"

    def test_jobmodel_str_method(self):
        Job.objects.create(
            title=self.title,
        )
        job_object = Job.objects.get(title=self.title)
        assert str(job_object) == job_object.title

    def test_jobmodel_get_absolute_url(self):
        url = Job.get_absolute_url(self)
        parsed_url = urlparse(url)
        query = urlencode({"q": self.title.lower()})
        assert isinstance(url, str)
        assert parsed_url.scheme == ""
        assert parsed_url.netloc == ""
        assert parsed_url.path == reverse("search_results")
        assert query in parsed_url.query


@pytest.mark.django_db
class TestSearchModel:
    def test_searchmodel_str_method(self):
        Search.objects.create(
            query="test search query",
            ip_address="9.9.9.9",
            user_agent="Test User-Agent",
        )
        search_object = Search.objects.get(ip_address="9.9.9.9")
        assert str(search_object) == search_object.query


@pytest.mark.django_db
class TestSkillModel:
    def test_skillmodel_str_method(self):
        test_name = "Test"
        Skill.objects.create(
            clean_name=test_name, unclean_names='["python", "python3", "phyton"]'
        )
        skill_object = Skill.objects.get(clean_name=test_name)
        assert str(skill_object) == skill_object.clean_name


class TestScrapersConfig:
    def test_scrapersconfig_name(self):
        app_path = Path(__file__).resolve().parent
        app_name = str(app_path).split("/")[-1]
        assert ScrapersConfig.name == app_name