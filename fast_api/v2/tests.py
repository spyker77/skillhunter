import pytest
from asgiref.sync import sync_to_async
from fastapi import Request
from starlette.datastructures import Headers

from scrapers.models import Search

from .background_tasks import save_query_with_meta_data
from .endpoints import skills


@pytest.mark.django_db
def test_show_skills(test_app, monkeypatch):
    def mock_save_query_with_meta_data(request, query):
        return None

    monkeypatch.setattr(skills, "save_query_with_meta_data", mock_save_query_with_meta_data)
    endpoint = "/api/v2/skills/"
    payload = {"q": "python developer", "limit": 20}
    query = payload.get("q")
    response = test_app.get(url=endpoint, params=payload, allow_redirects=True)
    assert response.status_code == 200
    assert response.json()["vacancy_name"] == query
    assert response.headers.get("content-type") == "application/json"
    # Check if the error response is correct.
    missing_required_param = {"q": ""}
    error_response = test_app.get(endpoint, params=missing_required_param)
    assert error_response.status_code == 404


@sync_to_async
def _check_scrapers_search_for_testclient_records() -> int:
    return Search.objects.filter(user_agent__icontains="testclient").count()


@sync_to_async
def _clean_db_after_tests() -> None:
    Search.objects.filter(user_agent__icontains="testclient").delete()


@pytest.mark.asyncio
async def test_save_query_with_meta_data(db):
    request = Request(scope={"type": "http", "headers": Headers({"user-agent": "testclient"}).raw})
    query = "python developer"
    initial_db_state = await _check_scrapers_search_for_testclient_records()
    await save_query_with_meta_data(request, query)
    assert await _check_scrapers_search_for_testclient_records() > initial_db_state
    await _clean_db_after_tests()


@pytest.mark.django_db
def test_show_tailored_vacancies_correct_resume(test_app):
    endpoint = "/api/v2/vacancies/"
    with open("resume_analyzer/test_resumes/correct_resume.pdf", "rb") as resume:
        response = test_app.post(url=endpoint, files={"resume": resume}, allow_redirects=True)
    number_of_default_vacancies = 200
    assert response.status_code == 200
    assert len(response.json()["vacancies"]) == number_of_default_vacancies


@pytest.mark.django_db
def test_show_tailored_vacancies_fake_resume(test_app):
    endpoint = "/api/v2/vacancies/"
    with open("resume_analyzer/test_resumes/fake_format.pdf", "rb") as resume:
        response = test_app.post(url=endpoint, files={"resume": resume}, allow_redirects=True)
    assert response.status_code == 404
    assert response.json()["detail"] == "Vacancies not found"


@pytest.mark.django_db
def test_show_tailored_vacancies_empty_resume(test_app):
    endpoint = "/api/v2/vacancies/"
    with open("resume_analyzer/test_resumes/empty_file.pdf", "rb") as resume:
        response = test_app.post(url=endpoint, files={"resume": resume}, allow_redirects=True)
    assert response.status_code == 200
    assert response.json()["vacancies"] == []
