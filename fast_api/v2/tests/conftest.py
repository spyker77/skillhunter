import pytest
from fastapi.testclient import TestClient

from fast_api.main import create_application

app = create_application()


@pytest.fixture(scope="module")
def test_app():
    with TestClient(app) as test_client:
        yield test_client
