from pathlib import Path
from urllib.parse import urlencode, urlparse

import pytest
from django.urls import reverse

from core.tasks import save_query_with_metadata

from .apps import ScrapersConfig
from .models import Job, Search, Skill, Vacancy
from .views import SearchResultsListView


@pytest.mark.django_db
class TestSearchResultsListView:
    url = reverse("search-results")
    data = {"q": "test search query"}
    query = data.get("q")
    ip_address = "9.9.9.9"
    x_forwarded_for = "90.90.90.90"
    user_agent = "Test User-Agent"

    @pytest.fixture
    def response(self, rf, monkeypatch):
        def mock_delay(query, user_agent, ip_address):
            return None

        monkeypatch.setattr(save_query_with_metadata, "delay", mock_delay)
        request = rf.get(
            self.url,
            self.data,
            follow=True,
            REMOTE_ADDR=self.ip_address,
            HTTP_USER_AGENT=self.user_agent,
        )
        response = SearchResultsListView.as_view()(request)
        return response

    @pytest.fixture
    def response_with_x_forwarded_for(self, rf, monkeypatch):
        def mock_delay(query, user_agent, ip_address):
            return None

        monkeypatch.setattr(save_query_with_metadata, "delay", mock_delay)
        request = rf.get(
            self.url,
            self.data,
            follow=True,
            HTTP_X_FORWARDED_FOR=self.x_forwarded_for,
            HTTP_USER_AGENT=self.user_agent,
        )
        response = SearchResultsListView.as_view()(request)
        return response

    def test_searchresultslistview_has_correct_status_code(self, response):
        assert response.status_code == 200

    def test_searchresultslistview_has_correct_status_code_when_ip_address_in_x_forwarded_for(
        self,
        response_with_x_forwarded_for,
    ):
        assert response_with_x_forwarded_for.status_code == 200

    def test_searchresultslistview_uses_correct_template(self, response):
        assert "search_results.html" in response.template_name

    def test_searchresultslistview_contains_correct_html(self, response):
        assert "Skills you need to be a" in response.rendered_content

    def test_searchresultslistview_does_not_contain_incorrect_html(self, response):
        assert "Hi there! I should not be on the page." not in response.rendered_content


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

    @pytest.fixture
    def job(self):
        return Job.objects.create(title=self.title)

    def test_jobmodel_str_method(self, job):
        assert str(job) == job.title

    def test_jobmodel_get_absolute_url(self, job):
        url = job.get_absolute_url()
        parsed_url = urlparse(url)
        query = urlencode({"q": self.title.lower()})
        assert isinstance(url, str)
        assert parsed_url.scheme == ""
        assert parsed_url.netloc == ""
        assert parsed_url.path == reverse("search-results")
        assert query in parsed_url.query


@pytest.mark.django_db
class TestSearchModel:
    def test_searchmodel_str_method(self):
        Search.objects.create(query="test search query", ip_address="0.0.0.0", user_agent="Test User-Agent")
        search_object = Search.objects.filter(ip_address="0.0.0.0")[0]
        assert str(search_object) == search_object.query


@pytest.mark.django_db
class TestSkillModel:
    def test_skillmodel_str_method(self):
        test_name = "Test"
        Skill.objects.create(clean_name=test_name, unclean_names=["python", "python3", "phyton"])
        skill_object = Skill.objects.get(clean_name=test_name)
        assert str(skill_object) == skill_object.clean_name


class TestScrapersConfig:
    def test_scrapersconfig_name(self):
        app_path = Path(__file__).resolve().parent
        app_name = str(app_path).split("/")[-1]
        assert ScrapersConfig.name == app_name
