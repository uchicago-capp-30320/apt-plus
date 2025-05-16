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

# Import model
from apt_app.models import TransitStop  # noqa: E402
from apt_app.models import TransitRoute  # noqa: E402


def create_cta_stop_from_row(row):
    """
    Convert a row from SQL database apt_app_cta_stops into a TransitStop
    instance (not saved yet).
    """
    cta_stop = TransitStop()

    # Name, type, and id
    cta_stop.name = row.get("stop_name", "")
    cta_stop.type = row.get("type", "")
    cta_stop.id = row.get("stop_id", "")

    # Location
    try:
        cta_stop.setup_location(row.get("latitude"), row.get("longitude"))
    except ValidationError as e:
        raise ValueError(f"Invalid location: {e}")

    return cta_stop


def create_cta_route_from_row(row):
    """
    Convert a row from SQL database apt_app_cta_routes into a TransitRoute
    instance (not saved yet).
    """
    cta_route = TransitRoute()

    # Name, type, and id
    cta_route.name = row.get("route_name", "")
    cta_route.type = row.get("type", "")
    cta_route.route_id = row.get("route_id", "")

    # Geometry
    geom = GEOSGeometry(row.get("geometry", ""))
    if geom.geom_type == "LineString":
        cta_route.geometry = MultiLineString(geom)
    elif geom.geom_type == "MultiLineString":
        cta_route.geometry = geom

    return cta_route


def create_route_stop_relationship_from_row(row, cta_stop_dict, cta_route_dict):
    """
    Create relationship between a route and a stop (for each row, not saved yet).
    """
    # access to table of relationships
    route_stop_db = TransitRoute.stops.through

    route_id = row.get("route_id", "")
    stop_id = row.get("stop_id", "")

    # look if corresponding ids exists routes and stops databases
    if route_id in cta_route_dict and stop_id in cta_stop_dict:
        cta_route = cta_route_dict[route_id]
        cta_stop = cta_stop_dict[stop_id]

        relationship = route_stop_db(transitroute_id=cta_route.route_id, transitstop_id=cta_stop.id)
        return relationship
    # print error messages in case that there is a mismatch of ids
    elif route_id not in cta_route_dict:
        print(f"Problem with route {route_id}")
        return None
    elif stop_id not in cta_stop_dict:
        print(f"Problem with bus stop {stop_id}")
        return None


def run_bulk_import(df, function_to_use, batch_size=1000):
    """
    Build and insert TransitStop or TransitRoutes objects in bulk to Django.
    For TransitStop, use the function "create_cta_stop_from_row".
    For TransitRoute, use the function "create_cta_route_from_row".
    """
    # Add new data
    print(f"Building objects for {len(df)} rows...")
    appended_rows = []

    # Get the route and stop ids from database for fast lookup in case of relationships data
    cta_route_dict = {route.route_id: route for route in TransitRoute.objects.all()}
    cta_stop_dict = {stop.id: stop for stop in TransitStop.objects.all()}

    for _, row in tqdm(df.iterrows(), total=len(df)):
        if function_to_use == create_route_stop_relationship_from_row:
            single_row = function_to_use(row, cta_stop_dict, cta_route_dict)
        else:
            single_row = function_to_use(row)
        if single_row:
            appended_rows.append(single_row)

    print(f"Inserting {len(appended_rows)} rows in bulk...")
    if function_to_use == create_cta_stop_from_row:
        # Ignore conflicts activated because stops are duplicated in this dataset,
        # because this dataset also has the relationship between stops and route
        TransitStop.objects.bulk_create(appended_rows, batch_size=batch_size, ignore_conflicts=True)
    elif function_to_use == create_cta_route_from_row:
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
    RouteStopRelationship.objects.all().delete()
    TransitStop.objects.all().delete()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM apt_app_transitroute;")

    # Routes - Read raw data from PostgreSQL table
    df_routes = pd.read_sql("SELECT * FROM apt_app_cta_routes", engine)

    # Import routes into Django model
    run_bulk_import(df_routes, create_cta_route_from_row)

    # Stops - Read raw data from PostgreSQL table
    df_stops = pd.read_sql("SELECT * FROM apt_app_cta_stops", engine)

    # Import stops into Django model
    run_bulk_import(df_stops, create_cta_stop_from_row)

    # Import relationships into Django model
    run_bulk_import(df_stops, create_route_stop_relationship_from_row)
