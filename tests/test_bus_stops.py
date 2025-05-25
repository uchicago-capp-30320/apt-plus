import pytest
from pytest_django.asserts import assertTemplateNotUsed
from apt_app.views.fetch_bus_stops import _fetch_bus_stops
from django.http import JsonResponse
import json


@pytest.mark.django_db
def test_fetch_bus_stops_response_structure():
    response = _fetch_bus_stops("41.795466862668, -87.590115956094 ", "35", 5)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    response_content = json.loads(response.content)

    # Test top-level structure
    assert "address" in response_content, "'address' field is missing from the response"
    assert "walking_time" in response_content, "'walking_time' field is missing from the response"
    assert "bus_stops_geojson" in response_content, (
        "'bus_stops_geojson' field is missing from the response"
    )

    # Test field types
    assert isinstance(response_content["address"], str), "'address' should be a string"
    assert isinstance(response_content["walking_time"], int), "'walking_time' should be an integer"
    assert isinstance(response_content["bus_stops_geojson"], dict), (
        "'bus_stops_geojson' should be a dictionary"
    )

    # Test bus_stops_geojson structure
    geojson = response_content["bus_stops_geojson"]
    assert geojson["type"] == "FeatureCollection", "GeoJSON type should be 'FeatureCollection'"
    assert "features" in geojson, "'features' array is missing from GeoJSON"
    assert isinstance(geojson["features"], list), "'features' should be a list"

    # Test at least one feature if features exist
    if geojson["features"]:
        feature = geojson["features"][0]
        assert feature["type"] == "Feature", "Feature type should be 'Feature'"

        # Test geometry
        assert "geometry" in feature, "'geometry' is missing from feature"
        assert feature["geometry"]["type"] == "Point", "Geometry type should be 'Point'"
        assert isinstance(feature["geometry"]["coordinates"], list), "Coordinates should be a list"
        assert len(feature["geometry"]["coordinates"]) == 2, (
            "Coordinates should have 2 elements [longitude, latitude]"
        )
        assert all(
            isinstance(coord, (int, float)) for coord in feature["geometry"]["coordinates"]
        ), "Coordinates should be numbers"

        # Test properties
        assert "properties" in feature, "'properties' is missing from feature"
        props = feature["properties"]
        assert "stop_name" in props, "'stop_name' is missing from properties"
        assert "distance_min" in props, "'distance_min' is missing from properties"
        assert "routes" in props, "'routes' is missing from properties"
        assert "stop_id" in props, "'stop_id' is missing from properties"

        # Test property types
        assert isinstance(props["stop_name"], str), "'stop_name' should be a string"
        assert isinstance(props["distance_min"], int), "'distance_min' should be an integer"
        assert isinstance(props["routes"], list), "'routes' should be a list"
        assert isinstance(props["stop_id"], str), "'stop_id' should be a string"


@pytest.mark.django_db
def test_fetch_bus_stops_response_no_stops():
    response = _fetch_bus_stops("-87.590115956094, 41.795466862668", "35", 5)
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"


@pytest.mark.django_db
def test_endpoint_available(client):
    """
    Test that the endpoint is available
    """
    response = client.get(
        "/fetch_bus_stops/",
        {"geocode": "41.795466862668, -87.590115956094", "property_id": "35", "walking_time": "5"},
    )
    assert response.status_code == 200, f"Response status code: {response.status_code} is not 200"
