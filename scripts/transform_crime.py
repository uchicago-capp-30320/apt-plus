import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import django
import pandas as pd
from sqlalchemy import create_engine
from django.core.exceptions import ValidationError
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import models
from apt_app.models import Crime, CrimeType # must be after django.setup()

def create_crime_from_row(row):
    """
    Convert a row from crimes_raw into a Crime instance (not saved yet).
    """
    crime = Crime()

    # Description
    crime.description = row.get("Description", "")

    # Date
    local_time = pd.to_datetime(row.get("Date", ""), errors="coerce")
    if pd.isna(local_time):
        raise ValueError("Invalid or missing date")
    crime.date = local_time.tz_localize("America/Chicago", ambiguous="NaT").tz_convert("UTC")

    # Crime type
    raw_type = row.get("Primary Type", "").strip().upper()
    crime.type = raw_type if raw_type in CrimeType.values else CrimeType.NON_CRIMINAL_ALT

    # Location
    try:
        crime.setup_location(row.get("Latitude"), row.get("Longitude"))
    except ValidationError as e:
        raise ValueError(f"Invalid location: {e}")

    return crime

def run_crime_import(df):
    """
    Save each row as a Crime object. Returns (success_count, failure_count).
    """
    success, failed = 0, 0
    total = len(df)
    print(f"Importing {total} rows...")

    for i, (_, row) in enumerate(df.iterrows(), 1):
        try:
            crime = create_crime_from_row(row)
            crime.save()
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
    df = pd.read_sql("SELECT * FROM apt_app_crime_raw", engine)

    # Import into Django model
    success, failed = run_crime_import(df)
    print(f"{success} rows imported successfully, {failed} failed.")
