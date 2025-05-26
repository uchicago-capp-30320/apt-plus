import pytest
from pytest_django.asserts import assertTemplateNotUsed
from apt_app.views.fetch_bus_routes import _fetch_bus_routes, _parse_input_routes
from django.http import JsonResponse
import json


def test_parse_input_routes():
    assert _parse_input_routes("171,172,55") == ["171", "172", "55"]
    assert _parse_input_routes(" 171 , 172 , 55 ") == ["171", "172", "55"]
    assert _parse_input_routes("  ") == []
    assert _parse_input_routes("") == []


@pytest.mark.django_db
def test_fetch_bus_routes_returns_valid_geojson_format():
    response = _fetch_bus_routes("5,171,28")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    response_content = json.loads(response.content)
    assert "type" in response_content, "'type' field is missing from the response"
    assert response_content["type"] == "FeatureCollection", (
        f"Expected 'FeatureCollection', got '{response_content.get('type')}'"
    )

    assert "features" in response_content, "'features' field is missing from the response"
    assert isinstance(response_content["features"], list), "'features' should be of type list"
    assert len(response_content["features"]) <= 3, "Number of features exceeds expected maximum"

    for i, feature in enumerate(response_content["features"]):
        assert "type" in feature, f"Feature at index {i} is missing 'type'"
        assert feature["type"] == "Feature", (
            f"Feature at index {i} has type '{feature['type']}' instead of 'Feature'"
        )
        assert "geometry" in feature, f"Feature at index {i} is missing 'geometry'"
        assert "properties" in feature, f"Feature at index {i} is missing 'properties'"

        props = feature["properties"]
        assert "route_id" in props, f"'route_id' missing in properties of feature at index {i}"
        assert "color" in props, f"'color' missing in properties of feature at index {i}"
        assert "name" in props, f"'name' missing in properties of feature at index {i}"
        assert "type" in props, f"'type' missing in properties of feature at index {i}"

        geos = feature["geometry"]
        assert "type" in geos, f"'type' missing in geometry of feature at index {i}"
        assert "coordinates" in geos, f"'coordinates' missing in geometry of feature at index {i}"
        assert isinstance(geos["coordinates"], list), (
            f"'coordinates' of feature at index {i} should be of type list"
        )


@pytest.mark.django_db
def test_fetch_bus_routes_returns_no_available():
    response = _fetch_bus_routes("500")
    assert response.status_code == 400, f"Expected 400 but got {response.status_code}"
    content = json.loads(response.content)
    assert "error" in content, "Missing 'error' in response content"


@pytest.mark.django_db
def test_endpoint_available(client):
    """
    Test that the endpoint is available
    """
    response = client.get("/fetch_bus_routes/", {"bus_route": "5,171"})
    assert response.status_code == 200, f"Response status code: {response.status_code} is not 200"
