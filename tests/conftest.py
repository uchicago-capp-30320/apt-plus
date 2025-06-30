import os
import pytest
from django.conf import settings


# Chat-GPT suggestion to avoid whitenoise static files, as playwright chromium
# browser can't access them for some reason
@pytest.fixture(autouse=True)
def override_staticfiles_storage(django_settings):
    django_settings.STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    django_settings.DEBUG = True


# Per: https://stackoverflow.com/a/78651148, this is fine to do iff for playwright
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
