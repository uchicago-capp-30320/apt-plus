import pytest
from apt_app.models import Property, Amenity, AmenityType
from django.contrib.gis.geos import Point


"""
WARNING:
Designed for test DB, but works on real DB too. Performs writes and deletes—use with caution.
"""

# Fixtures for properties
@pytest.fixture
def test_property_zero(db):
    prop = Property.objects.create(
        address="Zero Test St",
        location=Point(0.0, 0.0, srid=4326)
    )
    yield prop
    # prop.delete()

@pytest.fixture
def test_property_result(db):
    prop = Property.objects.create(
        address="Result Test St",
        location=Point(99.9999, 99.9999, srid=4326)
    )
    # https://docs.pytest.org/en/stable/how-to/fixtures.html#teardown-cleanup-aka-finalization
    yield prop
    # prop.delete()

@pytest.fixture
def test_property_cache(db):
    prop = Property.objects.create(
        address="Cache Test St",
        location=Point(99.9999, 99.9998, srid=4326)
    )
    yield prop
    # prop.delete()

# Fixture for 1 nearby grocery
@pytest.fixture
def test_grocery(db):
    grocery = Amenity.objects.create(
        name="Fake Grocery",
        type=AmenityType.GROCERY,
        location=Point(99.9998, 99.999, srid=4326),
        address="124 Test St"
    )
    yield grocery
    grocery.delete()


# Test 1: Zero results
@pytest.mark.django_db
def test_fetch_groceries_zero(client, test_property_zero):
    response = client.get(
        "/fetch_groceries/",
        {
            "geocode": "0.0,0.0",
            "walking_time": 0,
            "property_id": test_property_zero.id,
        },
    )
    data = response.json()
    assert response.status_code == 200
    assert len(data["grocery_geojson"]["features"]) == 0


# Test 2: One or more results
@pytest.mark.django_db
def test_fetch_groceries_returns_result(client, test_property_result, test_grocery):
    response = client.get(
        "/fetch_groceries/",
        {
            "geocode": "99.9999,99.9999",
            "walking_time": 15,
            "property_id": test_property_result.id,
        },
    )
    data = response.json()
    print("=== fetch_groceries_returns_result ===")
    print(data)
    assert response.status_code == 200
    assert len(data["grocery_geojson"]["features"]) > 0


# Test 3: Cache behavior
@pytest.mark.django_db
def test_fetch_groceries_cache(client, test_property_cache, test_grocery):
    # 1st call (triggers caching)
    response_1 = client.get(
        "/fetch_groceries/",
        {
            "geocode": "99.9999,99.9998",
            "walking_time": 15,
            "property_id": test_property_cache.id,
        },
    )
    data_1 = response_1.json()
    assert response_1.status_code == 200
    assert len(data_1["grocery_geojson"]["features"]) > 0

    # Fetch from DB and save cached version
    from apt_app.models import Property as PropertyModel
    cached = PropertyModel.objects.get(id=test_property_cache.id).groceries

    # 2nd call (should use cache → same result)
    response_2 = client.get(
        "/fetch_groceries/",
        {
            "geocode": "99.9999,99.9998",
            "walking_time": 15,
            "property_id": test_property_cache.id,
        },
    )
    data_2 = response_2.json()
    assert response_2.status_code == 200
    assert data_2 == cached


@pytest.mark.django_db
def test_endpoint_available(client, test_property_zero):
    """
    Test that the /fetch_groceries/ endpoint is available and responds with 200.
    """
    response = client.get(
        "/fetch_groceries/",
        {
            "geocode": "0.0,0.0",
            "walking_time": 15,
            "property_id": test_property_zero.id,
        },
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
