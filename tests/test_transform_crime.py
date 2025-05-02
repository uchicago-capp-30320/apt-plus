import pytest
from scripts.transform_crime import create_crime_from_row, run_crime_import
from apt_app.models import CrimeType
from unittest.mock import patch
import pandas as pd

def base_row(**overrides):
    """
    Helper to create a full crimes_raw-like row with realistic defaults,
    override any field by passing it as a keyword argument.
    """
    row = {
        "ID": 13311263,
        "Case Number": "JG503434",
        "Date": "07/29/2022 03:39:00 AM",
        "Block": "023XX S TROY ST",
        "IUCR": "1582",
        "Primary Type": "THEFT",
        "Description": "OVER $500",
        "Location Description": "SIDEWALK",
        "Arrest": True,
        "Domestic": False,
        "Beat": 1234,
        "District": 12.0,
        "Ward": 25.0,
        "Community Area": 30.0,
        "FBI Code": "17",
        "X Coordinate": 1170000.0,
        "Y Coordinate": 1900000.0,
        "Year": 2022,
        "Updated On": "04/18/2024 03:40:59 PM",
        "Latitude": 41.881,
        "Longitude": -87.623,
        "Location": "(41.881, -87.623)"
    }
    row.update(overrides)
    return row

# --- Test: successful creation ---
def test_valid_row_creates_crime():
    row = base_row()
    crime = create_crime_from_row(row)
    assert crime.type == CrimeType.THEFT
    assert crime.location.y == 41.881
    assert crime.location.x == -87.623
    assert crime.description == "OVER $500"

# --- Test: unknown Primary Type falls back ---
def test_unknown_primary_type_fallbacks():
    row = base_row(**{"Primary Type": "UNKNOWN CRIME"})
    crime = create_crime_from_row(row)
    assert crime.type == CrimeType.NON_CRIMINAL_ALT

# --- Test: invalid date raises error ---
def test_invalid_date_raises():
    row = base_row(**{"Date": "not-a-date"})
    with pytest.raises(ValueError, match="Invalid or missing date"):
        create_crime_from_row(row)

# --- Test: missing latitude raises error ---
def test_missing_latitude_raises():
    row = base_row(**{"Latitude": None})
    with pytest.raises(ValueError, match="Invalid location"):
        create_crime_from_row(row)

# --- Integration: one good + one bad row ---
@patch("apt_app.models.Crime.save")
def test_run_crime_import_with_realistic_rows(mock_save):
    df = pd.DataFrame([
        base_row(),  # valid
        base_row(**{"Latitude": "not-a-number"})  # invalid
    ])
    success, failed = run_crime_import(df)
    assert success == 1
    assert failed == 1
    mock_save.assert_called_once()
