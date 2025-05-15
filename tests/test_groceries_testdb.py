# need to be fixed

import pytest
from django.db import connections
from django.test import Client
from django.conf import settings


@pytest.fixture(scope="session", autouse=True)
def django_db_setup():
    settings.DATABASES["default"]["NAME"] = "test_app_dev"

@pytest.mark.django_db
def test_fetch_groceries_zero():
    client = Client()
    response = client.post("/fetch_groceries/", {
        "geocode": "0.0,0.0",
        "walking_time": 5,
        "property_id": 1,
    })
    data = response.json()
    assert response.status_code == 200
    assert len(data["grocery_geojson"]["features"]) == 0

@pytest.mark.django_db
def test_fetch_groceries_hyde_park():
    client = Client()
    response = client.post("/fetch_groceries/", {
        "geocode": "41.7943,-87.5907",  # Hyde Park
        "walking_time": 15,
        "property_id": 1,
    })
    data = response.json()
    print("=== fetch_groceries_hyde_park ===")
    print(data)
    assert response.status_code == 200
    assert len(data["grocery_geojson"]["features"]) > 0
