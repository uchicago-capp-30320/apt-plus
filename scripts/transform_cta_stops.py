import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import django
import pandas as pd
from sqlalchemy import create_engine
from django.core.exceptions import ValidationError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import model
from apt_app.models import TransitStop  # must be after django.setup()


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


def run_import(df):
    """
    Save each row. Returns (success_count, failure_count).
    """
    success, failed = 0, 0
    total = len(df)
    print(f"Importing {total} rows...")

    for i, (_, row) in enumerate(df.iterrows(), 1):
        try:
            cta_stop = create_cta_stop_from_row(row)
            cta_stop.save()
            success += 1
        except Exception as e:
            print(f"[Row {i}] Skipped due to error: {e}")
            failed += 1

        if i % 100 == 0 or i == total:
            print(f"[{i}/{total}] Processed...")

    return success, failed


if __name__ == "__main__":
    # Read from database using connection string from .env
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)

    # Read raw data from PostgreSQL table
    df = pd.read_sql("SELECT * FROM apt_app_cta_stops", engine)

    # Import into Django model
    success, failed = run_import(df)
    print(f"{success} rows imported successfully, {failed} failed.")
