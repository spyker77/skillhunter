import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestSkillViewSet:
    url = reverse("api:skill-list")
    data = {"q": "python developer", "limit": 20, "format": "json"}
    query = data.get("q")
    ip_address = "9.9.9.9"
    user_agent = "Test User-Agent"

    @pytest.fixture(autouse=True)
    def override_redis_cache(self, settings):
        settings.CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.dummy.DummyCache",
            }
        }

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

    def test_skillviewset_status_code(self, response):
        assert response.status_code == 200

    def test_skillviewset_correct_data_content(self, response):
        assert response.json()["vacancy_name"] == self.query

    def test_skillviewset_correct_data_format(self, response):
        assert "application/json" in str(response)