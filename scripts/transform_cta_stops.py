import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import django
import pandas as pd
from sqlalchemy import create_engine
from django.core.exceptions import ValidationError
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import model
from apt_app.models import TransitStop  # noqa: E402


def create_cta_stop_from_row(row):
    """
    Convert a row from SQL database apt_app_cta_stops into a TransitStop instance (not saved yet).
    """
    cta_stop = TransitStop()

    # Name
    cta_stop.name = row.get("name", "")

    # Type
    cta_stop.type = row.get("type", "")

    # Location
    try:
        cta_stop.setup_location(row.get("latitude"), row.get("longitude"))
    except ValidationError as e:
        raise ValueError(f"Invalid location: {e}")

    return cta_stop


def run_bulk_import(df, batch_size=1000):
    """
    Build and insert TransitStop objects in bulk to Django .
    """
    # Delete previous data
    TransitStop.objects.all().delete()

    # Add new data
    print(f"Building objects for {len(df)} rows...")
    cta_stops = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        single_stop = create_cta_stop_from_row(row)
        if single_stop:
            cta_stops.append(single_stop)

    print(f"Inserting {len(cta_stops)} rows in bulk...")
    TransitStop.objects.bulk_create(cta_stops, batch_size=batch_size)
    print("Done.")


if __name__ == "__main__":
    # Read from database using connection string from .env
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)

    # Read raw data from PostgreSQL table
    df = pd.read_sql("SELECT * FROM apt_app_cta_stops", engine)

    # Import into Django model
    run_bulk_import(df)
