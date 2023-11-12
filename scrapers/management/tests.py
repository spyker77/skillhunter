import pytest

from .utils import get_user_agent, get_webdriver


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


def test_get_webdriver():
    with get_webdriver() as driver:
        # Check WebDriver is initialized correctly.
        assert driver.service is not None
        assert driver.capabilities["browserName"] == "firefox"

        # WebDriver should still be operational at this point.
        assert driver.service.is_connectable()

    # WebDriver should be closed after exiting the context.
    assert not driver.service.is_connectable()
