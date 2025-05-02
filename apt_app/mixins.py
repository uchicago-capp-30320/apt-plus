from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError


class LocationMixin:
    def setup_location(self, lat, lon, srid=4326):
        try:
            lat = float(lat)
            lon = float(lon)
            self.location = Point(lon, lat, srid=srid)
        except (TypeError, ValueError):
            raise ValidationError("Invalid latitude/longitude values")
