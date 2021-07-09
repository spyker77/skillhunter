import pytest

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
