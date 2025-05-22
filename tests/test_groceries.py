import pytest
from django.db import connections
from django.test import Client

"""
WARNING:
This test uses the actual (non-test) database. Make sure your test
only performs read operations, or be fully aware of the risks if it involves writing data.
"""

# Test that when querying with coordinates (0.0, 0.0), no groceries are returned.
@pytest.mark.django_db
def test_fetch_groceries_zero(client):
    response = client.get("/fetch_groceries/", {
        "geocode": "0.0,0.0",       # Random location in the ocean
        "walking_time": 5,
        "property_id": 1,
    })
    data = response.json()
    assert response.status_code == 200
    assert len(data["grocery_geojson"]["features"]) == 0  # Expecting no results

# Test that groceries near Hyde Park are returned when using valid coordinates.
@pytest.mark.django_db
def test_fetch_groceries_hyde_park(client):
    response = client.get("/fetch_groceries/", {
        "geocode": "41.7943,-87.5907",  # Center of Hyde Park, Chicago
        "walking_time": 15,
        "property_id": 1,
    })
    data = response.json()
    print("=== fetch_groceries_hyde_park ===")
    print(data)
    assert response.status_code == 200
    assert len(data["grocery_geojson"]["features"]) > 0  # Expecting results nearby

@pytest.mark.django_db
def test_endpoint_available(client):
    """
    Test that the /fetch_groceries/ endpoint is available and responds with 200.
    """
    response = client.get("/fetch_groceries/", {
        "geocode": "0.0,0.0",       # Random location in the ocean
        "walking_time": 5,
        "property_id": 1,
    })
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
