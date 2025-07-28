import json
import os
import pytest
import re
import time
from playwright.sync_api import Page
from django.core import mail


@pytest.fixture(autouse=True)
def override_staticfiles_storage(settings):
    """
    Chat-GPT suggestion to avoid whitenoise static files, as playwright
    chromium # browser can't access them for some reason
    """
    settings.STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    settings.DEBUG = True
    # Allows email access in tests
    # Ref: https://docs.djangoproject.com/en/5.2/topics/email/#email-backends
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


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


# Helper code for authentication
def get_verification_code_from_email() -> str:
    """
    Returns the first 6-digit code from the body of the most recent email.
    Raises an error if no emails exist or no code is found.

    Inputs:
        - None

    Returns: (str) The verification code for email validation
    """
    start = time.time()
    while time.time() - start < 5:
        if mail.outbox:
            latest_email = mail.outbox[-1]
            match = re.search(r"\b(\d{6})\b", latest_email.body)
            if match:
                return match.group(1)
        time.sleep(1)
    raise RuntimeError("No email with 6-digit code found after waiting")


def authenticate_email(page: Page, live_server):
    """
    Function to authenticate Aptpl.us and then save the cookie into local
    storage that is git ignored
    """
    # TODO: Try sign-up flow, not log-in flow as user not in database
    # Alt: Add user to data base as:

    storage_path = os.path.join("tests", ".auth", "cookies.json")
    page.goto(live_server.url)
    page.wait_for_load_state()

    try:
        # Submit request
        if page.locator("#djHideToolBarButton"):
            page.locator("#djHideToolBarButton").click()
        page.locator("#nav-log-in").click()
        page.wait_for_load_state()
        page.locator("#id_login").fill("test_email@aptpl.us")
        page.locator("#id_remember").click()  # Select remember me to save cookie
        page.get_by_role("button", name="Sign In").click()

        # Grab verification code and complete
        page.wait_for_load_state("networkidle")  # To send email
        print("=" * 40)
        print("mail.outbox length:", len(mail.outbox))

        if mail.outbox:
            latest = mail.outbox[-1]
            print("Subject:", latest.subject)
            print("To:", latest.to)
            print("Body:", latest.body)
        else:
            print("mail.outbox is empty")

        print("=" * 40)

        code = get_verification_code_from_email()
        page.locator("#id_code").fill(code)
        page.get_by_role("button", name="Confirm").click()

        # Save cookies after redirect completed
        page.wait_for_load_state()
        page.context.storage_state(path=storage_path)
    except Exception as e:
        raise RuntimeError(f"Failed to log in and save auth state: {e}")

    return None


def check_auth_dir():
    """
    Checks if the .auth directory exsts with files inside it. If there
    are files, continues to authenticated.
    """
    # Check if .auth dir exists
    root = os.path.dirname(os.path.abspath(__file__))
    auth_dir = os.path.join(root, ".auth")
    if not os.path.isdir(auth_dir):
        os.mkdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".auth"))
        return False

    # Check for any file in the .auth directory
    for fname in os.listdir(auth_dir):
        fpath = os.path.join(auth_dir, fname)
        if os.path.isfile(fpath):
            return True

    return False


@pytest.fixture()
def authenticated(page: Page, live_server):
    """
    Fixture to use authentication.

    Means that all calls to a page would instead go to the authenticated page
    object for tests that use this fixture.
    """
    # First check the auth directory exists
    if not check_auth_dir():
        # Fill email
        authenticate_email(page, live_server)

    # THen grab cookie file
    cookie = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".auth", "authenticated.json")

    # Else use cookie
    with open(cookie, "r") as f:
        cookie = json.load(f)
    page.context.add_cookies(cookie)
    return page
