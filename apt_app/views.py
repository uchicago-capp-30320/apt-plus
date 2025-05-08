from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceRatio
from apt_app.models import TransitStop, Property
from django.contrib.gis.db.models.functions import Distance as DistanceFunction


def home(request):
    return render(request, "home.html")


def fetch_bus_stops(request):
    """Take property location and desired walking distance,
    return disticnt bus stops within the walking distance.
    Update property table with the bus stops."""

    geocode = request.GET.get("geocode")
    lat_str, lon_str = geocode.split(",")
    lat, lon = float(lat_str), float(lon_str)
    walking_time = int(request.GET.get("walking_time", 5))  # default 5 min
    property_id = request.GET.get("property_id")

    # borrow code from Miguel's scripts/check_data_cta_ctops.py refactor later
    # Distance in meters, GoogleMaps has a walking time of 4.2 km per hour.
    ratio_in_meters = walking_time / 60 * 4200

    reference_point = Point(lat, lon, srid=4326)
    # find stops within ratio_in_meters from the reference point
    near_stops = TransitStop.objects.filter(
        location__distance_lte=(reference_point, DistanceRatio(m=ratio_in_meters))
    )
    # generate distance between each stop and reference point
    near_stops = near_stops.annotate(distance=DistanceFunction("location", reference_point))

    # keep only closest stop for each name by using order_by and distinct
    # NOTE: "Order_by" sorts the bus_stops by name and distance (closest stops first),
    # and "distinct" keeps only the closest bus_stop by name.
    near_stops = near_stops.order_by("name", "distance").distinct("name")

    prop = Property.objects.get(id=property_id)
    clean_address = prop.address
    features = []
    for stop in near_stops:
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [stop.location.x, stop.location.y],
                },
                "properties": {
                    # "stop_name": stop.name,
                    "distance_min": round(stop.distance.m / 70),  # 70 m/min
                    "routes": stop.name,
                    "stop_id": stop.id,
                },
            }
        )
    ## update property table
    prop.bus_stops = features
    prop.save()

    response = {
        "address": clean_address,
        "walking_time": walking_time,
        "bus_stops_geojson": {
            "type": "FeatureCollection",
            "features": features,
        },
    }

    return JsonResponse(response)
