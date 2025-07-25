import os
import pytest


@pytest.fixture(autouse=True)
def override_staticfiles_storage(settings):
    """
    Chat-GPT suggestion to avoid whitenoise static files, as playwright
    chromium # browser can't access them for some reason
    """
    settings.STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    settings.DEBUG = True


# Per: https://stackoverflow.com/a/78651148, this is fine to do iff for playwright
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


# Add options to not run playwright except when added
# From: https://github.com/Chris-May/django_playwright_pytest_example/blob/main/tests/conftest.py
def pytest_addoption(parser):
    """Looks for the `runplaywright` argument"""
    parser.addoption(
        "--runplaywright",
        action="store_true",
        default=False,
        help="run playwright tests",
    )


def pytest_configure(config):
    """Auto-add the slow mark to the config at runtime"""
    config.addinivalue_line("markers", "playwright: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    """This skips the tests if --runplaywright is not present"""
    if config.getoption("--runplaywright"):
        return
    skip_slow = pytest.mark.skip(reason="need --runplaywright option to run")
    for item in items:
        if "playwright" in item.keywords:
            item.add_marker(skip_slow)
