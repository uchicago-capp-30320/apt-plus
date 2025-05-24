import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceRatio
from apt_app.models import TransitStop, Property
from django.contrib.gis.db.models.functions import Distance as DistanceFunction
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from .fetch_all_data import _fetch_all_data
from .fetch_groceries import _fetch_groceries
from .fetch_bus_stops import _fetch_bus_stops
from .fetch_inspections import _fetch_inspection_summaries
from .fetch_bus_routes import _fetch_bus_routes


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


@csrf_exempt
@require_GET
def fetch_all_data(request):
    address = request.GET.get("address")
    return _fetch_all_data(address)


@require_GET
def fetch_groceries(request):
    # extract parameters from request
    geocode = request.GET.get("geocode")
    walking_time = int(request.GET.get("walking_time", 5))
    return _fetch_groceries(geocode, walking_time)


@require_GET
def fetch_bus_stops(request):
    geocode = request.GET.get("geocode")
    walking_time = int(request.GET.get("walking_time", 5))  # default 5 min
    property_id = request.GET.get("property_id")
    return _fetch_bus_stops(geocode, property_id, walking_time)


@require_GET
def fetch_inspections(request):
    address = request.GET.get("address", "")
    return _fetch_inspection_summaries(address)


@require_GET
def fetch_bus_routes(request):
    route_id = request.GET.get("bus_route")
    return _fetch_bus_routes(route_id)


# TODO: this should be moved elsewhere since it is a hard-coded mock
# -- maybe should be in tests but not sure
def fetch_all_data_mock(request):
    address = request.GET.get("address", "")

    print(address)

    # Generating a sample geojson response with a point lying inside
    # Hyde Park, Chicago
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-87.591848, 41.801696]},
                "properties": {"name": "Hyde Park, Chicago"},
            }
        ],
    }
    # Convert the dictionary to a JSON string before returning
    return HttpResponse(json.dumps(geojson), content_type="application/json")
