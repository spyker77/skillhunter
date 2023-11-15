import pytest
from django.urls import reverse

from core.tasks import save_query_with_metadata


@pytest.mark.django_db
class TestTailoredSkillsViewSet:
    url = reverse("tailored-skills" + "-" + "list")
    data = {"q": "python developer", "limit": 20, "format": "json"}
    query = data.get("q")
    ip_address = "1.1.1.1"
    x_forwarded_for = "10.10.10.10"
    user_agent = "Test User-Agent"

    @pytest.fixture(autouse=True)
    def override_redis_cache(self, settings):
        settings.CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}

    @pytest.fixture
    def response(self, client, monkeypatch):
        def mock_delay(query, user_agent, ip_address):
            return None

        monkeypatch.setattr(save_query_with_metadata, "delay", mock_delay)
        response = client.get(
            path=self.url,
            data=self.data,
            follow=True,
            REMOTE_ADDR=self.ip_address,
            HTTP_USER_AGENT=self.user_agent,
        )
        return response

    @pytest.fixture
    def response_with_x_forwarded_for(self, client, monkeypatch):
        def mock_delay(query, user_agent, ip_address):
            return None

        monkeypatch.setattr(save_query_with_metadata, "delay", mock_delay)
        response = client.get(
            path=self.url,
            data=self.data,
            follow=True,
            HTTP_X_FORWARDED_FOR=self.x_forwarded_for,
            HTTP_USER_AGENT=self.user_agent,
        )
        return response

    def test_tailoredskillsviewset_has_correct_status_code(self, response):
        assert response.status_code == 200

    def test_tailoredskillsviewset_has_correct_status_code_when_ip_address_in_x_forwarded_for(
        self,
        response_with_x_forwarded_for,
    ):
        assert response_with_x_forwarded_for.status_code == 200

    def test_tailoredskillsviewset_has_correct_data_content(self, response):
        assert response.json()["vacancy_name"] == self.query

    def test_tailoredskillsviewset_has_correct_data_format(self, response):
        assert "application/json" in str(response)


@pytest.mark.django_db
class TestTailoredVacanciesViewSet:
    url = reverse("tailored-vacancies" + "-" + "list")

    @pytest.fixture(autouse=True)
    def override_redis_cache(self, settings):
        settings.CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}

    def test_tailoredvacanciesviewset_with_correct_resume(self, client):
        with open("resume_analyzer/test_resumes/correct_resume.pdf", "rb") as resume:
            response = client.post(path=self.url, data={"resume": resume}, secure=True)
        assert response.status_code == 200
        assert response.json() != []

    def test_tailoredvacanciesviewset_with_fake_resume(self, client):
        with open("resume_analyzer/test_resumes/fake_format.pdf", "rb") as resume:
            response = client.post(path=self.url, data={"resume": resume}, secure=True)
        assert response.status_code == 400
        assert response.json()["detail"] == "Error processing resume."

    def test_tailoredvacanciesviewset_with_empty_resume(self, client):
        with open("resume_analyzer/test_resumes/empty_file.pdf", "rb") as resume:
            response = client.post(path=self.url, data={"resume": resume}, secure=True)
        assert response.status_code == 200
        assert response.json() == []
