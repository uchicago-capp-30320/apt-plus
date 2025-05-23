from django.http import JsonResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceRatio
from apt_app.models import TransitStop, Property, TransitRoute
from django.contrib.gis.db.models.functions import Distance as DistanceFunction
from config import load_constants
from django.db.models import Prefetch

CONSTANTS = load_constants()
WALKING_METERS_PER_MIN = CONSTANTS["WALKING_METERS_PER_MIN"]


def _fetch_bus_stops(geocode, property_id, walking_time=5):
    """Take property location and desired walking distance,
    return disticnt bus stops within the walking distance.
    Update property table with the bus stops."""
    try:
        lon_str, lat_str = geocode.split(",")
        lon, lat = float(lon_str), float(lat_str)
    except Exception as e:
        print(f"error: Failure in parsing request: {str(e)}")
        return JsonResponse({"error": f"Failure in parsing request: {str(e)}"}, status=400)

    # borrow code from Miguel's scripts/check_data_cta_ctops.py refactor later
    # Distance in meters, GoogleMaps has a walking time of 4.2 km per hour.
    try:
        ratio_in_meters = walking_time * WALKING_METERS_PER_MIN
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
            .prefetch_related(
                ## why dont keep distinct route id here:
                # could be different directions of the same route
                Prefetch(
                    "routes",
                    queryset=TransitRoute.objects.only("route_id"),
                )
            )
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
                        "stop_name": stop.name,
                        "distance_min": round(stop.distance.m / WALKING_METERS_PER_MIN),  # 70 m/min
                        "routes": [route.route_id for route in stop.routes.all()],
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
