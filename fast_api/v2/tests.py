import pytest


@pytest.mark.django_db
def test_show_skills(test_app):
    endpoint = "/api/v2/skills/"
    params = {"q": "python developer", "limit": 20}
    query = params.get("q")
    response = test_app.get(endpoint, params=params)
    assert response.status_code == 200
    assert response.json()["vacancy_name"] == query
    assert response.headers.get("content-type") == "application/json"
    # Check if the error response is correct.
    missing_required_param = {"q": ""}
    error_response = test_app.get(endpoint, params=missing_required_param)
    assert error_response.status_code == 404
