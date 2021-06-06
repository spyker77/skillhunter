import pytest
from django.core.cache import cache
from django.urls import reverse

from resume_analyzer.forms import UploadResumeForm
from resume_analyzer.views import upload_resume


@pytest.mark.django_db
class TestUploadResumeCorrect:
    @pytest.fixture(autouse=True)
    def override_redis_cache(self, settings):
        settings.CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

    @pytest.fixture
    def rq(self, rf):
        with open("resume_analyzer/test_resumes/correct_resume.pdf", "rb") as resume:
            request = rf.post(reverse("tailored_vacancies"), data={"resume": resume})
        return request

    @pytest.fixture
    def response(self, rq):
        response = upload_resume(rq)
        return response

    def test_uploadresumecorrect_form_valid(self, rq):
        posted_resume_form = UploadResumeForm(rq.POST, rq.FILES)
        assert posted_resume_form.is_valid() is True

    def test_uploadresumecorrect_status_code(self, response):
        assert response.status_code == 200

    def test_uploadresumecorrect_contains_correct_html(self, response):
        assert "Vacancies tailored to your resume" in response.content.decode()

    def test_uploadresumecorrect_does_not_contain_incorrect_html(self, response):
        assert "Hi there! I should not be on the page." not in response.content.decode()

    def test_uploadresumecorrect_does_not_contain_error_message(self, response):
        assert "Please, make sure" not in response.content.decode()

    def test_uploadresumecorrect_is_not_empty(self, response):
        assert "Oh no, it looks like we can’t tailor vacancies right now..." not in response.content.decode()

    def test_uploadresumecorrect_returns_vacancies(self, response):
        assert "python developer" in response.content.decode().lower()

    def test_uploadresumecorrect_cache_contains_skills(self, response):
        assert cache.get("skills_from_db") is not None

    def test_uploadresumecorrect_cache_contains_vacancies(self, response):
        assert cache.get("vacancies") is not None


@pytest.mark.django_db
class TestUploadResumeFake:
    @pytest.fixture
    def rq(self, rf):
        with open("resume_analyzer/test_resumes/fake_format.pdf", "rb") as resume:
            request = rf.post(reverse("tailored_vacancies"), data={"resume": resume})
        return request

    @pytest.fixture
    def response(self, rq):
        response = upload_resume(rq)
        return response

    def test_uploadresumefake_form_valid(self, rq):
        posted_resume_form = UploadResumeForm(rq.POST, rq.FILES)
        assert posted_resume_form.is_valid() is True

    def test_uploadresumefake_status_code(self, response):
        assert response.status_code == 200

    def test_uploadresumefake_contains_correct_html(self, response):
        assert "Please, make sure" in response.content.decode()

    def test_uploadresumefake_does_not_contain_incorrect_html(self, response):
        assert "Hi there! I should not be on the page." not in response.content.decode()


@pytest.mark.django_db
class TestUploadResumeEmpty:
    @pytest.fixture
    def rq(self, rf):
        with open("resume_analyzer/test_resumes/empty_file.pdf", "rb") as resume:
            request = rf.post(reverse("tailored_vacancies"), data={"resume": resume})
        return request

    @pytest.fixture
    def response(self, rq):
        response = upload_resume(rq)
        return response

    def test_uploadresumeempty_form_valid(self, rq):
        posted_resume_form = UploadResumeForm(rq.POST, rq.FILES)
        assert posted_resume_form.is_valid() is True

    def test_uploadresumeempty_status_code(self, response):
        assert response.status_code == 200

    def test_uploadresumeempty_contains_correct_html(self, response):
        assert "Oh no, it looks like we can’t tailor vacancies right now..." in response.content.decode()

    def test_uploadresumeempty_does_not_contain_incorrect_html(self, response):
        assert "Hi there! I should not be on the page." not in response.content.decode()
