from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.views.decorators.csrf import csrf_exempt
from apt_app.models import Amenity, AmenityType, Property
from config import load_constants

CONSTANTS = load_constants()
WALKING_METERS_PER_MIN = CONSTANTS["WALKING_METERS_PER_MIN"]


def _fetch_groceries(geocode: str, property_id: str, walking_time: int = 15) -> JsonResponse:
    if not property_id:
        return JsonResponse({"error": "property_id is required"}, status=400)
    if not geocode:
        return JsonResponse({"error": "geocode is required"}, status=400)

    try:
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

        # cache to Property
        try:
            prop = Property.objects.get(id=property_id)
            response["address"] = prop.address
            if not prop.groceries:
                prop.groceries = response
                prop.save()
        except Property.DoesNotExist:
            return JsonResponse({"error": "Property not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Failed to update Property: {str(e)}"}, status=400)

        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
