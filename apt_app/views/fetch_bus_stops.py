from django.http import JsonResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceRatio
from apt_app.models import TransitStop, Property, TransitRoute
from django.contrib.gis.db.models.functions import Distance as DistanceFunction
from config import load_constants
from django.db.models import Prefetch

CONSTANTS = load_constants()
WALKING_METERS_PER_MIN = CONSTANTS["WALKING_METERS_PER_MIN"]


def _fetch_bus_stops(geocode: str, property_id: str, walking_time: int = 5):
    """Take property location and desired walking distance,
    return disticnt bus stops within the walking distance.
    Update property table with the bus stops."""
    if not property_id:
        print("error: property_id is required")
        return JsonResponse({"error": "property_id is required"}, status=400)
    if not geocode:
        print("error: geocode is required")
        return JsonResponse({"error": "geocode is required"}, status=400)
    if not walking_time:
        print("error: walking_time is required")
        return JsonResponse({"error": "walking_time is required"}, status=400)
    if walking_time < 0:
        print("error: walking_time must be greater than 0")
        return JsonResponse({"error": "walking_time must be greater than 0"}, status=400)

    try:
        lon_str, lat_str = geocode.split(",")
        lon, lat = float(lon_str), float(lat_str)
    except Exception as e:
        print(f"error: Failure in parsing request: {str(e)}")
        return JsonResponse({"error": f"Failure in parsing request: {str(e)}"}, status=400)

    # borrow code from Miguel's scripts/check_data_cta_ctops.py refactor later
    # Distance in meters, GoogleMaps has a walking time of 4.2 km per hour.
    try:
        walking_time = int(walking_time)
        ratio_in_meters = walking_time * WALKING_METERS_PER_MIN
        reference_point = Point(lat, lon, srid=4326)
        # find stops within ratio_in_meters from the reference point
        near_stops = (
            TransitStop.objects.filter(
                location__distance_lte=(reference_point, DistanceRatio(m=ratio_in_meters))
            )
            .annotate(distance=DistanceFunction("location", reference_point))
            .prefetch_related(
                Prefetch(
                    "routes",
                    queryset=TransitRoute.objects.only("route_id"),
                )
            )
        )
    except Exception as e:
        return JsonResponse({"error": f"Failure in querying bus stop data: {str(e)}"}, status=400)
    if not near_stops:
        return JsonResponse({"error": "No bus stops found within the walking distance"}, status=400)

    # get property object
    try:
        prop = Property.objects.get(id=property_id)
    except Exception as e:
        return JsonResponse({"error": f"Invalid property_id: {str(e)}"}, status=400)

    # format response
    try:
        clean_address = prop.address
    except Exception as e:
        return JsonResponse({"error": f"No address info in property table: {str(e)}"}, status=400)

    try:
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
                        "stop_name": stop.name,
                        "distance_min": round(stop.distance.m / WALKING_METERS_PER_MIN),  # 70 m/min
                        "routes": [route.route_id for route in stop.routes.all()],
                        "stop_id": str(stop.id),
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
            prop.bus_stops = response
            prop.save()
    except Exception as e:
        return JsonResponse({"error": f"Failed to update property table: {str(e)}"}, status=400)

    return JsonResponse(response)
