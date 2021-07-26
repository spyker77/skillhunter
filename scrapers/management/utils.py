import platform

from faker import Faker


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
