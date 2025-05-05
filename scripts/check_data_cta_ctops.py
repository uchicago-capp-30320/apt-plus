import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import model
from apt_app.models import TransitStop  # must be after django.setup()
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceRatio
from django.contrib.gis.db.models.functions import Distance as DistanceFunction


# Function to check data in the Django dataset
def check_general_data():
    """
    Helper function that check generally that the data from cta stops is in the
    Django dataset. It print those checks, returns None.
    """
    # Start time
    start_time = time.perf_counter()

    # Count observations
    total_stops = TransitStop.objects.count()
    print(f"Total observations in TransitStops: {total_stops}")

    # Check first 10 observations
    first_stops = TransitStop.objects.all()[:10]
    print("\nFirst 10 transit stops:")
    for stop in first_stops:
        print(f"ID: {stop.id}, Name: {stop.name}, Type: {stop.type}, Location: ({stop.location})")

    # Time running time
    end_time = time.perf_counter()
    print(f"Execution time of general tests: {end_time - start_time:.2f} seconds")


def stops_near_a_point(latitude_input, longitude_input, walking_time_input):
    """
    Function that print the bus stops within walking time related to a reference point.
    Returns None.
    """
    # Start time
    start_time = time.perf_counter()
    print(
        f"Stops within {walking_time_input} minutes of coordinates {latitude_input}N, {longitude_input}W"
    )

    # Distance in meters, GoogleMaps has a walking time of 4.2 km per hour.
    ratio_in_meters = walking_time_input / 60 * 4200

    # Reference point and find stops within 100 meters
    ## NOTE: For reference, the distance_lte command from Django is explained in Link 1,
    ## distance_lte section.The general code to perform spatial queries is explained in
    ## Link 2, section "Performing Spatial Queries"
    ## Link 1: https://docs.djangoproject.com/en/5.2/ref/contrib/gis/geoquerysets/#std-fieldlookup-distance_lte
    ## Link 2: https://medium.com/@limeira.felipe94/geodjango-101-how-to-add-maps-and-spatial-data-to-your-django-projects-e3617fb51474
    reference_point = Point(latitude_input, longitude_input, srid=4326)
    near_stops = TransitStop.objects.filter(
        location__distance_lte=(reference_point, DistanceRatio(m=ratio_in_meters))
    )
    # generate distance between each stop and reference point
    ## NOTE: The distance between 2 points is calculated using the "annotate" function
    ## with DistanceFunction. The documentation is available in the "Distance" section
    ## of link 1.
    ## Link 1: https://docs.djangoproject.com/en/5.2/ref/contrib/gis/functions/
    near_stops = near_stops.annotate(distance=DistanceFunction("location", reference_point))

    # keep only closest stop for each name by using order_by and distinct
    ## NOTE: "Order_by" sorts the bus_stops by name and distance (closest stops first),
    ## and "distinct" keeps only the closest bus_stop by name.
    ## Link:
    near_stops = near_stops.order_by("name", "distance").distinct("name")
    # print results
    for stop in near_stops:
        print(
            f"Stop ID: {stop.id}, Name: {stop.name}, Type: {stop.type}, Location: {stop.location}, Distance (meters): {stop.distance.m}"
        )

    # Time running time
    end_time = time.perf_counter()
    print(f"Execution time of stops near specific point: {end_time - start_time:.2f} seconds")


# Run the code
if __name__ == "__main__":
    check_general_data()
    # Example: Closest bus stops to 55th and S Hyde Park Blvd.
    latitude_example = -87.58420643801648
    longitude_example = 41.795416711406915
    walking_time_example = 1
    stops_near_a_point(latitude_example, longitude_example, walking_time_example)
