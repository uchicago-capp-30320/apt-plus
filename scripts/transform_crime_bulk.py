import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import django
import pandas as pd
from sqlalchemy import create_engine
from django.core.exceptions import ValidationError
from dotenv import load_dotenv
import pytz
from dateutil import tz
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import models
from apt_app.models import Crime, CrimeType # must be after django.setup()

def create_crime_object(row):
    """
    Convert a row from crimes_raw into a Crime instance.
    """
    try:
        crime = Crime()
        crime.description = row.get("Description", "")

        # Date
        local_time = pd.to_datetime(row.get("Date", ""), errors="coerce")
        if pd.isna(local_time):
            return None
        central = tz.gettz("America/Chicago")
        local_time = local_time.replace(tzinfo=central)
        crime.date = local_time.astimezone(pytz.UTC)

        # Crime type
        raw_type = row.get("Primary Type", "").strip().upper()
        crime.type = raw_type if raw_type in CrimeType.values else CrimeType.NON_CRIMINAL_ALT

        # Location
        crime.setup_location(row.get("Latitude"), row.get("Longitude"))

        return crime
    except Exception:
        return None

def run_bulk_import(df, batch_size=1000):
    """
    Build and insert Crime objects in bulk.
    """
    print(f"Building objects for {len(df)} rows...")
    crimes = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        crime = create_crime_object(row)
        if crime:
            crimes.append(crime)

    print(f"Inserting {len(crimes)} rows in bulk...")
    Crime.objects.bulk_create(crimes, batch_size=batch_size)
    print("Done.")

if __name__ == "__main__":
    # Read from database using connection string from .env
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    # Read raw data from PostgreSQL table
    df = pd.read_sql("SELECT * FROM apt_app_crime_raw", engine)
    run_bulk_import(df)
