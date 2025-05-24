from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.views.decorators.csrf import csrf_exempt
from apt_app.models import Amenity, AmenityType
from config import load_constants

CONSTANTS = load_constants()
