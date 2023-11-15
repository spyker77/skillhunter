import pytest
from playwright.sync_api import Error, Page

from .utils import get_playwright_page, get_user_agent


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


def test_get_playwright_page():
    with get_playwright_page() as page:
        assert isinstance(page, Page)

    # After the context manager exits, the page should be closed.
    with pytest.raises(Error):
        _ = page.title()
