import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import django
from dotenv import load_dotenv
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceRatio
from django.contrib.gis.db.models.functions import Distance as DistanceFunction
import logging
from django.db.models import Prefetch
from django.core.serializers import serialize


# Load environment variables
load_dotenv()

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import model (after setup of django)
from apt_app.models import TransitStop  # noqa: E402
from apt_app.models import TransitRoute  # noqa: E402

# Set up logging
logging.basicConfig(
    level=logging.INFO,
)
logging.getLogger().setLevel(logging.WARNING)
logger = logging.getLogger("")


# Function to check data in the Django dataset
def check_general_data():
    """
    Helper function that check generally that the data from cta stops is in the
    Django dataset. It print those checks, returns None.
    """
    # Start time
    start_time = time.perf_counter()

    # Count observations - Bus Stops
    total_stops = TransitStop.objects.count()
    print(f"Total observations in TransitStops: {total_stops}")

    # Check first 5 observations - Bus Stops
    first_stops = TransitStop.objects.all()[:5]
    logger.info("\nFirst 5 transit stops:")
    for stop in first_stops:
        logger.info(
            f"ID: {stop.id}, Name: {stop.name}, Type: {stop.type}, Location: ({stop.location})"
        )

    # Count observations - Routes
    total_routes = TransitRoute.objects.count()
    print(f"Total observations in TransitRoutes: {total_routes}")

    # Check first 3 observations - Routes
    first_routes = TransitRoute.objects.all()[:3]
    logger.info("\nFirst 3 transit routes:")
    for route in first_routes:
        logger.info(f"ID: {route.route_id}, Name: {route.name}, Type: {route.type}")

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
    # Generate distance between each stop and reference point
    ## NOTE: The distance between 2 points is calculated using the "annotate" function
    ## with DistanceFunction. The documentation is available in the "Distance" section
    ## of link 1.
    ## Link 1: https://docs.djangoproject.com/en/5.2/ref/contrib/gis/functions/
    near_stops = near_stops.annotate(distance=DistanceFunction("location", reference_point))
    print(f"Number of nearby stops: {near_stops.count()}")

    # Get the relationship considerably faster between bus stop and route id with
    # prefetch_related and only
    ## NOTE: I checked the use of prefecth_related and only on Django documentation,
    ## particularly, links 1 and 2.
    ## Link 1: https://docs.djangoproject.com/en/5.2/ref/models/querysets/#prefetch-related
    ## Link 2: https://docs.djangoproject.com/en/5.2/ref/models/querysets/#only
    near_stops = near_stops.prefetch_related(
        Prefetch(
            "routes",
            queryset=TransitRoute.objects.only("route_id"),
        )
    )
    # Log results
    for stop in near_stops:
        # get bus stop
        logger.info(
            f"ID: {stop.id}, Name: {stop.name}, Type: {stop.type}, "
            + f"Location: {stop.location}, Distance (meters): {stop.distance.m:.1f}"
        )
        # get the routes related to that stop
        route_ids = [route.route_id for route in stop.routes.all()]
        logger.info(f"The routes of this stop are {route_ids}")

    # Total time of function
    end_time = time.perf_counter()
    print(
        f"Execution time of stops {walking_time_input} minutes near specific point: "
        f"{end_time - start_time:.2f} seconds"
    )


def get_route_line(route_ids_list):
    """
    Function that print the route MultiLineString related to the list route_ids_list.
    Returns None.
    """
    # Start time
    start_time = time.perf_counter()

    # Serialize the data to get the GeoJSON format
    ## NOTE: I check the documentation related to GeoJSON serializer to check
    ## how to use it.
    ## Link: https://docs.djangoproject.com/en/5.1/ref/contrib/gis/serializers/
    ## NOTE 2: THe "pk" parameter is the primary key, that in this case is the route_id,
    ## and is useful for having that primary key inside the "properties" of the json.
    geojson_output = serialize(
        "geojson",
        TransitRoute.objects.filter(route_id__in=route_ids_list),
        geometry_field="geometry",
        fields=("route_id", "name", "type", "pk"),
    )
    logger.info(geojson_output)

    # Total time of function
    end_time = time.perf_counter()
    print(
        f"Execution time of getting route lines of routes {route_ids_list}: "
        f"{end_time - start_time:.2f} seconds"
    )


# Define auxiliar variables to run the code (optional to activate more addresses for check)
address_references = [
    ("55th and S Hyde Park Blvd", -87.58420643801648, 41.795416711406915),
    ("55th and S Woodlawn Ave", -87.596472, 41.794889),
    # ("E Hyde Park Blvd and S Kenwood Ave", -87.593418, 41.802277),
    # ("123 S Clark St, at Chicago Downtown", -87.63045, 41.87962),
    # ("E Randolph St with N State St", -87.62784, 41.88447),
    # ("N Michigan Ave with E Ontario St", -87.62444, 41.89343),
]

# Run the code to check that is working properly
if __name__ == "__main__":
    # Get multilinestring related to CTA routes, compare time of one and multiple routes
    route_ids_list = ["171"]
    get_route_line(route_ids_list)
    route_ids_list = ["171", "172", "192", "2", "6", "15", "28", "55"]
    get_route_line(route_ids_list)

    # Check time of retrieval of multilinestring related to Shuttle routes
    route_ids_list = [
        "53rd Street Express",
        "Apostolic",
        "Apostolic/Drexel",
        "Downtown Connector",
        "Drexel",
        "Friend Center/Metra",
        "Red Line/Arts Block",
        # 'Midway Metra',
    ]
    get_route_line(route_ids_list)

    # Check time for general data
    check_general_data()

    # Time for reference addresses, 15 minutes
    for address, latitude, longitude in address_references:
        print(address)
        walking_time_example = 15
        stops_near_a_point(latitude, longitude, walking_time_example)

    # Time for reference addresses, 2 minutes
    for address, latitude, longitude in address_references:
        print(address)
        walking_time_example = 2
        stops_near_a_point(latitude, longitude, walking_time_example)
