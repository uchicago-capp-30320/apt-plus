import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceRatio
from apt_app.models import TransitStop, Property
from django.contrib.gis.db.models.functions import Distance as DistanceFunction
from django.views.decorators.csrf import csrf_exempt
from apt_app.views_functions.function_fetch_all_data import fetching_all_data

WALKING_SPEED_PER_MINUTE = 70


def home(request):
    # todo
    print(request.user)
    return render(request, "home.html")


def fetch_bus_stops(request):
    """Take property location and desired walking distance,
    return disticnt bus stops within the walking distance.
    Update property table with the bus stops."""
    try:
        geocode = request.GET.get("geocode")
        lon_str, lat_str = geocode.split(",")
        lon, lat = float(lon_str), float(lat_str)
        walking_time = int(request.GET.get("walking_time", 5))  # default 5 min
        property_id = request.GET.get("property_id")
    except Exception as e:
        print(f"error: Failure in parsing request: {str(e)}")
        return JsonResponse({"error": f"Failure in parsing request: {str(e)}"}, status=400)

    # borrow code from Miguel's scripts/check_data_cta_ctops.py refactor later
    # Distance in meters, GoogleMaps has a walking time of 4.2 km per hour.
    try:
        ratio_in_meters = walking_time * WALKING_SPEED_PER_MINUTE
        reference_point = Point(lat, lon, srid=4326)
        # find stops within ratio_in_meters from the reference point
        # keep only closest stop for each name by using order_by and distinct
        # NOTE: "Order_by" sorts the bus_stops by name and distance (closest stops first),
        # and "distinct" keeps only the closest bus_stop by name.
        near_stops = (
            TransitStop.objects.filter(
                location__distance_lte=(reference_point, DistanceRatio(m=ratio_in_meters))
            )
            .annotate(distance=DistanceFunction("location", reference_point))
            .order_by("name", "distance")
            .distinct("name")
        )
    except Exception as e:
        print(f"error: Failure in querying bus stop data: {str(e)}")
        return JsonResponse({"error": f"Failure in querying bus stop data: {str(e)}"}, status=400)
    try:
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
        response = {
            "address": clean_address,
            "walking_time": walking_time,
            "bus_stops_geojson": {
                "type": "FeatureCollection",
                "features": features,
            },
        }

        ## update property table
        if not prop.bus_stops:
            print("no records in the cache table, updating:")
            prop.bus_stops = features
            prop.save()
            print("property table updated")
    except Exception as e:
        print(f"error: Failure in updating cache table: {str(e)}")
        return JsonResponse({"error": f"Failure in updating cache table: {str(e)}"}, status=400)

    return JsonResponse(response)


def about(request):
    return render(request, "about.html")


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


@csrf_exempt
def fetch_all_data(request):
    address = request.GET.get("address")
    json_response = fetching_all_data(address)
    return json_response
