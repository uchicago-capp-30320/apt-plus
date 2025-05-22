import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from dotenv import load_dotenv
load_dotenv()
import django
django.setup()
from apt_app.models import Amenity, AmenityType
import pandas as pd
from sqlalchemy import create_engine
from tqdm import tqdm

# === CONFIGURATION ===
TARGET_RAW_TYPES = {
    "grocery_or_supermarket",
}

RAW_TO_AMENITY_TYPE = {
    "grocery_or_supermarket": AmenityType.GROCERY,
}

# === SETUP ===
load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# === FUNCTIONS ===
def create_amenity_object(row, amenity_type):
    try:
        amenity = Amenity()
        amenity.name = row.get("name", "")
        amenity.type = amenity_type
        amenity.setup_location(row.get("lat"), row.get("lng"))
        amenity.address = row.get("address","")
        return amenity
    except Exception as e:
        print("Row skipped due to error:", e)
        return None

def run_bulk_import(df, amenity_type, batch_size=500):
    print(f"Building objects for {len(df)} rows of type '{amenity_type}'...")
    amenities = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        amenity = create_amenity_object(row, amenity_type)
        if amenity:
            amenities.append(amenity)

    print(f"Inserting {len(amenities)} rows in bulk...")
    Amenity.objects.bulk_create(amenities, batch_size=batch_size)
    print("Done.")

# === MAIN ===
if __name__ == "__main__":
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)

    for raw_type in TARGET_RAW_TYPES:
        if raw_type not in RAW_TO_AMENITY_TYPE:
            print(f"[SKIP] Unknown raw type: {raw_type}")
            continue

        amenity_type = RAW_TO_AMENITY_TYPE[raw_type]

        df = pd.read_sql(f"""
            SELECT * FROM apt_app_amenity_raw
            WHERE type = '{raw_type}'
        """, engine)

        if df.empty:
            print(f"[INFO] No data found for raw type: {raw_type}")
            continue

        run_bulk_import(df, amenity_type)
