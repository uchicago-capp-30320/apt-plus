import pytest
from django.db import connections
from django.test import Client

"""
WARNING:
This test uses the actual (non-test) database. Make sure your test
only performs read operations, or be fully aware of the risks if it involves writing data.
"""
# This fixture monkey-patches Django's test database creation/destruction.
# It prevents Pytest from creating a separate test DB and instead uses the real one.
@pytest.fixture(autouse=True, scope="module")
def prevent_test_db_creation():
    for conn in connections.all():
        conn.creation.create_test_db = lambda *args, **kwargs: conn.settings_dict["NAME"]
        conn.creation.destroy_test_db = lambda *args, **kwargs: None

# Test that when querying with coordinates (0.0, 0.0), no groceries are returned.
@pytest.mark.django_db
def test_fetch_groceries_zero():
    client = Client()
    response = client.post("/fetch_groceries/", {
        "geocode": "0.0,0.0",       # Random location in the ocean
        "walking_time": 5,
        "property_id": 1,
    })
    data = response.json()
    assert response.status_code == 200
    assert len(data["grocery_geojson"]["features"]) == 0  # Expecting no results

# Test that groceries near Hyde Park are returned when using valid coordinates.
@pytest.mark.django_db
def test_fetch_groceries_hyde_park():
    client = Client()
    response = client.post("/fetch_groceries/", {
        "geocode": "41.7943,-87.5907",  # Center of Hyde Park, Chicago
        "walking_time": 15,
        "property_id": 1,
    })
    data = response.json()
    print("=== fetch_groceries_hyde_park ===")
    print(data)
    assert response.status_code == 200
    assert len(data["grocery_geojson"]["features"]) > 0  # Expecting results nearby
