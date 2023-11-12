import platform
from contextlib import contextmanager

from faker import Faker
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService


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
def get_webdriver():
    # Initializes and returns a WebDriver instance with specific options for Firefox.
    service = FirefoxService(log_path="/dev/null")
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.set_preference("general.useragent.override", get_user_agent())
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)

    driver = Firefox(service=service, options=options)
    driver.maximize_window()

    try:
        yield driver
    finally:
        driver.quit()
