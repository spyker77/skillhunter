import pytest

from .utils import get_user_agent


@pytest.mark.parametrize(
    "os_name, expected_agent",
    [
        ("darwin", "Mac"),
        ("windows", "Windows"),
        ("linux", "Linux"),
    ],
)
def test_get_user_agent(monkeypatch, os_name, expected_agent):
    monkeypatch.setattr("platform.system", lambda: os_name)
    user_agent = get_user_agent()
    assert expected_agent in user_agent
