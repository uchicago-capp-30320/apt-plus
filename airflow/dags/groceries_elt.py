import requests
import psycopg2
import json
from datetime import datetime
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
from airflow.decorators import dag, task

# Load environment variables from .env
load_dotenv()

@dag(
    dag_id="grocery_elt_pipeline",
    schedule="@monthly",
    start_date=datetime(2025, 5, 1),
    catchup=False,
    tags=["elt", "grocery"]
)
def grocery_elt_pipeline():

    @task
    def extract():
        """
        Extract grocery store data from Chicago's Open Data portal (GeoJSON).
        """
        url = 'https://data.cityofchicago.org/resource/3e26-zek2.geojson'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["features"]

    @task
    def transform(features):
        """
        Transform raw GeoJSON into structured records and load into staging_grocery.
        """
        db_url = os.getenv("_DEFAULT_DB")
        parsed = urlparse(db_url)
        conn = psycopg2.connect(
            dbname=parsed.path.lstrip("/"),
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port
        )
        cur = conn.cursor()

        # Create staging table (for filtered, normalized grocery data)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS staging_grocery (
                id TEXT PRIMARY KEY,
                store_name TEXT,
                address TEXT,
                zip TEXT,
                longitude DOUBLE PRECISION,
                latitude DOUBLE PRECISION,
                status TEXT,
                last_updated TIMESTAMP
            )
        """)

        # Truncate for full refresh
        cur.execute("TRUNCATE TABLE staging_grocery")

        # Insert transformed records
        # Ref: https://www.postgresql.org/docs/current/functions-json.html
        cur.execute("""
            INSERT INTO staging_grocery (
                id, store_name, address, zip, longitude, latitude, status, last_updated
            )
            SELECT
                -- Create unique ID: address + lon + lat
                (f->'properties'->>'address') || '|' ||
                (f->'geometry'->'coordinates'->0)::text || '|' ||
                (f->'geometry'->'coordinates'->1)::text AS id,
                f->'properties'->>'store_name',
                f->'properties'->>'address',
                f->'properties'->>'zip',
                (f->'geometry'->'coordinates'->0)::text::FLOAT,
                (f->'geometry'->'coordinates'->1)::text::FLOAT,
                f->'properties'->>'new_status',
                NULLIF(f->'properties'->>'last_updated', '')::TIMESTAMP
            FROM jsonb_array_elements(%s::jsonb) AS raw(f)
            WHERE f->'properties'->>'address' IS NOT NULL
              AND UPPER(f->'properties'->>'new_status') = 'OPEN'
              AND jsonb_typeof(f->'geometry') = 'object'
              AND jsonb_array_length(f->'geometry'->'coordinates') = 2
        """, (json.dumps(features),))

        conn.commit()
        cur.close()
        conn.close()

    @task
    def merge():
        """
        Merge staging_grocery into final apt_app_amenity table.
        """
        db_url = os.getenv("_DEFAULT_DB")
        parsed = urlparse(db_url)
        conn = psycopg2.connect(
            dbname=parsed.path.lstrip("/"),
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port
        )
        cur = conn.cursor()

        # Insert/Update grocery records into Amenity table
        cur.execute("""
            INSERT INTO apt_app_amenity (name, address, location, type)
            SELECT
                s.store_name,
                s.address,
                ST_SetSRID(ST_MakePoint(s.longitude, s.latitude), 4326),
                'grocery'
            FROM staging_grocery s
            ON CONFLICT (address, type) DO UPDATE
            SET
                name = EXCLUDED.name,
                location = EXCLUDED.location
            WHERE
                apt_app_amenity.name IS DISTINCT FROM EXCLUDED.name OR
                apt_app_amenity.location IS DISTINCT FROM EXCLUDED.location
        """)

        # Delete any outdated grocery entries
        cur.execute("""
            DELETE FROM apt_app_amenity
            WHERE type = 'grocery'
            AND (address || '|' || ST_X(location) || '|' || ST_Y(location)) NOT IN (
                SELECT address || '|' || longitude || '|' || latitude FROM staging_grocery
            )
        """)

        conn.commit()
        cur.close()
        conn.close()

    # Define task dependencies
    features = extract()
    transform(features)
    merge()

dag = grocery_elt_pipeline()
