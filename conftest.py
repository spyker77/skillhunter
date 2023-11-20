import logging

import pytest
from django.core.management import call_command
from django.db.utils import IntegrityError


def _prepopulate_database(django_db_blocker):
    with django_db_blocker.unblock():
        try:
            # Provide initial data for tests.
            call_command("loaddata", "jobs.json")
            call_command("loaddata", "skills.json")
            call_command("loaddata", "scrapers_vacancy.json")
            # Split to reduce the size of a single potentially huge file and not pay for Git LFS. Use it if
            # you need more data for tests. The file above contains 9999 records while below is an
            # additional 29997 – so in total there can be 39996 vacancies.
            # call_command("loaddata", "scrapers_vacancy_part_1.json")
            # call_command("loaddata", "scrapers_vacancy_part_2.json")
            # call_command("loaddata", "scrapers_vacancy_part_3.json")
        except IntegrityError:
            # Data is already in the database.
            pass


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    # Notice django_db_setup in the argument – it triggers the original pytest-django fixture to create the
    # test database, so that when call_command is invoked, the test database is already prepared and configured.
    _prepopulate_database(django_db_blocker)


@pytest.fixture(autouse=True)
def enable_log_propagation():
    loggers = ["celery", "django"]
    original_propagation_settings = {}

    # Store original propagation settings and enable propagation.
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        original_propagation_settings[logger_name] = logger.propagate
        logger.propagate = True

    yield

    # Reset to original propagation settings after the test.
    for logger_name, original_setting in original_propagation_settings.items():
        logger = logging.getLogger(logger_name)
        logger.propagate = original_setting
