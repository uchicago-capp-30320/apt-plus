from dotenv import load_dotenv
import pytest
from django.contrib.gis.geos import Point, LineString
from apt_app.models import Property, TransitStop, TransitRoute
from apt_app.views.fetch_bus_stops import _fetch_bus_stops
from django.http import JsonResponse
import json

load_dotenv()


### load fake testing data:
@pytest.mark.django_db
def test_fetch_bus_stops_success():
    """
    prop = Property.objects.create(
            address="123 Test st",
            location=Point(-87.6007, 41.7934)
        )

    stop1 = TransitStop.objects.create(
            name="Test Stop A",
            location=Point(-87.5990, 41.7944), # close stop
            type="cta"
        )

    stop2 = TransitStop.objects.create(
            name="Test Stop B",
            location=Point(-87.5965, 41.7960), # far stop
            type="cta"
        )

    route = TransitRoute.objects.create(
            name="Route 55",
            type="cta",
            geometry=LineString([(-87.5990, 41.7944), (-87.5965, 41.7960)])
        )

    route.stops.add(stop1, stop2)
    """

    geocode = "41.7934,-87.6007"  # latitude, longitude
    response = _fetch_bus_stops(geocode, property_id=7, walking_time=5)
    assert isinstance(response, JsonResponse)
    data = json.loads(response.content)
    print("=== fetch_bus_stops ===")
    print(data)
    assert response.status_code == 200
    assert len(data["bus_stops_geojson"]["features"]) > 0
    # assert data["address"] == "123 Test Ave"
    # assert len(data["bus_stops_geojson"]["features"]) == 1
    for stop in data["bus_stops_geojson"]["features"]:
        assert stop.get("type")
        assert stop.get("geometry")
        assert stop.get("properties")

        assert stop["properties"].get("stop_name")
        assert stop["properties"].get("routes")
        assert stop["properties"].get("distance_min")
        assert stop["properties"].get("stop_id")
