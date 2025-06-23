import os

# Per: https://stackoverflow.com/a/78651148, this is fine to do iff for playwright
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE","true")
