import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import django
import pandas as pd
from sqlalchemy import create_engine
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import GEOSGeometry, MultiLineString
from dotenv import load_dotenv
from tqdm import tqdm
from django.db import connection

# Load environment variables
load_dotenv()

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import model (after setup of django)
from apt_app.models import TransitStop  # noqa: E402
from apt_app.models import TransitRoute  # noqa: E402


def create_stop_from_row(row):
    """
    Convert a row from SQL database apt_app_stops into a TransitStop
    instance (not saved yet).

    Inputs:
        row (pandas Series): row from a pandas dataframe related to the SQL
            database apt_app_stops.

    Returns: a TransitStop instance.
    """
    single_stop = TransitStop()

    # Name, type, and id
    single_stop.name = row.get("stop_name", "")
    single_stop.type = row.get("type", "")
    single_stop.id = row.get("stop_id", "")

    # Location
    try:
        single_stop.setup_location(row.get("latitude"), row.get("longitude"))
    except ValidationError as e:
        raise ValueError(f"Invalid location: {e}")

    return single_stop


def create_route_from_row(row):
    """
    Convert a row from SQL database apt_app_routes into a TransitRoute
    instance (not saved yet).

    Inputs:
        row (pandas Series): row from a pandas dataframe related to the SQL
            database apt_app_routes.

    Returns: a TransitRoute instance.
    """
    single_route = TransitRoute()

    # Name, type, and id
    single_route.name = row.get("route_name", "")
    single_route.type = row.get("type", "")
    single_route.route_id = row.get("route_id", "")

    # Geometry
    geom = GEOSGeometry(row.get("geometry", ""))
    if geom.geom_type == "LineString":
        single_route.geometry = MultiLineString(geom)
    elif geom.geom_type == "MultiLineString":
        single_route.geometry = geom

    return single_route


def create_route_stop_relationship_from_row(row, stop_dict, route_dict):
    """
    Create relationship between a route and a stop (for each row, not saved yet).

    Inputs:
        row (pandas Series): row from a pandas dataframe related to the SQL
            database apt_app_stops.
        stop_dict (dict): dictionary of available stops in the data.
        route_dict (dict): dictionary of available routes in the data.

    Returns: a relationship instance between the TransitRoute and TransitStop tables.
    """
    # Access to table of relationships
    route_stop_db = TransitRoute.stops.through

    route_id = str(row.get("route_id", ""))
    stop_id = str(row.get("stop_id", ""))

    # Look if corresponding ids exists routes and stops databases
    if route_id in route_dict and stop_id in stop_dict:
        single_route = route_dict[route_id]
        single_stop = stop_dict[stop_id]

        relationship = route_stop_db(
            transitroute_id=single_route.route_id, transitstop_id=single_stop.id
        )
        return relationship
    # Print error messages in case that there is a mismatch of ids
    elif route_id not in route_dict:
        print(f"Problem with route {route_id}")
        return None
    elif stop_id not in stop_dict:
        print(f"Problem with bus stop {stop_id}")
        return None


def run_bulk_import(
    df,
    function_to_use,
    stop_dict=None,
    route_dict=None,
    batch_size=1000,
):
    """
    Build and insert TransitStop and TransitRoutes objects or relationships
    between them in bulk to Django data model. Particularly:
        - For upload TransitStop objects, use the function "create_stop_from_row".
        - For upload TransitRoute objects, use the function "create_route_from_row".
        - For generating relationships between TransitStop and TransitRoute, use the
            function "create_route_stop_relationship_from_row" and provide the corresponding
            dictionaries of stops and routes as an input.

    Inputs:
        df (Pandas dataframe): dataframe that contains the data that is going to be used
            by the function to be called.
        function_to_use (function): function to be used to upload data.
        stop_dict (dict): dictionary of available stops in the data, only used in
            "create_route_stop_relationship_from_row" function, None by default.
        route_dict (dict): dictionary of available routes in the data, only used in
            "create_route_stop_relationship_from_row" function, None by default.
        batch_size (int): batch size to use, 1000 by default.

    Returns: None
    """
    # Add new data
    print(f"Building objects for {len(df)} rows...")
    appended_rows = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        if function_to_use == create_route_stop_relationship_from_row:
            single_row = function_to_use(row, stop_dict, route_dict)
        else:
            single_row = function_to_use(row)
        if single_row:
            appended_rows.append(single_row)

    print(f"Inserting {len(appended_rows)} rows in bulk...")
    if function_to_use == create_stop_from_row:
        # Ignore conflicts activated because stops are duplicated in this dataset,
        # makes sense because this dataset also has the relationship between stops and route
        TransitStop.objects.bulk_create(appended_rows, batch_size=batch_size, ignore_conflicts=True)
    elif function_to_use == create_route_from_row:
        TransitRoute.objects.bulk_create(
            appended_rows, batch_size=batch_size, ignore_conflicts=True
        )
    elif function_to_use == create_route_stop_relationship_from_row:
        route_stop_db = TransitRoute.stops.through
        route_stop_db.objects.bulk_create(
            appended_rows, batch_size=batch_size, ignore_conflicts=True
        )
    print("Done.")


if __name__ == "__main__":
    # Read from database using connection string from .env
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)

    # Delete previous data
    RouteStopRelationship = TransitRoute.stops.through
    deleted_relationships = RouteStopRelationship.objects.all().delete()
    deleted_stops = TransitStop.objects.all().delete()
    deleted_routes = TransitRoute.objects.all().delete()

    # Routes - Read raw data from PostgreSQL table
    df_routes = pd.read_sql("SELECT * FROM apt_app_routes", engine)

    # Import routes into Django model
    run_bulk_import(df_routes, create_route_from_row)

    # Stops - Read raw data from PostgreSQL table
    df_stops = pd.read_sql("SELECT * FROM apt_app_stops", engine)

    # Import stops into Django model
    run_bulk_import(df_stops, create_stop_from_row)

    # Generate dictionaries to do relationships faster
    stop_dict = {str(stop.id): stop for stop in TransitStop.objects.all()}
    route_dict = {str(route.route_id): route for route in TransitRoute.objects.all()}

    # Import relationships into Django model
    run_bulk_import(df_stops, create_route_stop_relationship_from_row, stop_dict, route_dict)
