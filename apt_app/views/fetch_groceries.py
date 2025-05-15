from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.views.decorators.csrf import csrf_exempt
from apt_app.models import Amenity, AmenityType
from config import load_constants

CONSTANTS = load_constants()
WALKING_METERS_PER_MIN = CONSTANTS["WALKING_METERS_PER_MIN"]


def _fetch_groceries(geocode, walking_time=5) -> JsonResponse:
    try:
        # NOTE:
        # _ = request.GET.get("property_id")  # placeholder for future caching

        # Convert geocode to Point
        lat_str, lng_str = geocode.split(",")
        property_location = Point(float(lng_str), float(lat_str), srid=4326)

        # Convert walking time to distance
        walking_distance = walking_time * WALKING_METERS_PER_MIN

        # Query nearby groceries
        groceries = (
            Amenity.objects.filter(type=AmenityType.GROCERY)
            .annotate(distance=Distance("location", property_location))
            .filter(distance__lte=walking_distance)
            .order_by("distance")
        )

        # Build GeoJSON features
        features = []
        for g in groceries:
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [g.location.x, g.location.y],
                    },
                    "properties": {
                        "name": g.name,
                        "distance_min": round(g.distance.m / WALKING_METERS_PER_MIN, 1),
                        "address": getattr(g, "address", ""),
                    },
                }
            )

        geojson = {
            "type": "FeatureCollection",
            "features": features,
        }

        # Return JSON response
        response = {
            "address": "",
            "walking_time": walking_time,
            "grocery_geojson": geojson,
        }

        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
