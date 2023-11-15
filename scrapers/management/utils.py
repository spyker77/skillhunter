import platform
from contextlib import contextmanager

from faker import Faker
from playwright.sync_api import sync_playwright


def get_user_agent():
    # Generate user-agent appropriate for the platform.
    faker = Faker()
    os_name = platform.system().lower()
    if os_name == "darwin":
        while True:
            user_agent = faker.firefox()
            if "Mac" in user_agent:
                return user_agent
    elif os_name == "windows":
        while True:
            user_agent = faker.firefox()
            if "Windows" in user_agent:
                return user_agent
    else:
        while True:
            user_agent = faker.firefox()
            if "Linux" in user_agent:
                return user_agent


@contextmanager
def get_playwright_page():
    # Initializes Playwright and yields new page.
    playwright = sync_playwright().start()
    browser = playwright.firefox.launch(headless=True)
    context = browser.new_context(user_agent=get_user_agent(), viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    try:
        yield page
    finally:
        page.close()
        context.close()
        browser.close()
        playwright.stop()
