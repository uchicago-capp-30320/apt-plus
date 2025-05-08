from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.views.decorators.csrf import csrf_exempt


from apt_app.models import Amenity, AmenityType

WALKING_SPEED_PER_MIN = 80  # Average walking speed in meters per minute
# https://en.wikipedia.org/wiki/Preferred_walking_speed?utm_source=chatgpt.com

@csrf_exempt
@require_POST
def fetch_groceries(request):
    try:
        # Extract parameters from request
        geocode = request.POST.get('geocode')
        walking_time = int(request.POST.get('walking_time', 5))
        _ = request.POST.get('property_id') # placeholder for future caching

        # Convert geocode to Point
        lat_str, lng_str = geocode.split(',')
        property_location = Point(float(lng_str), float(lat_str), srid=4326)

        # Convert walking time to distance
        walking_distance = walking_time * WALKING_SPEED_PER_MIN

        # Query nearby groceries
        groceries = (
            Amenity.objects
            .filter(type=AmenityType.GROCERY)
            .annotate(distance=Distance('location', property_location))
            .filter(distance__lte=walking_distance)
            .order_by('distance')
        )

        # Build GeoJSON features
        features = []
        for g in groceries:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [g.location.x, g.location.y],
                },
                'properties': {
                    'name': g.name,
                    'distance_min': round(g.distance.m / WALKING_SPEED_PER_MIN, 1),
                    'address': getattr(g, 'address', ''),
                },
            })

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
