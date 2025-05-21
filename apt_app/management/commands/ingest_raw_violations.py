import os
import csv
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from apt_app.models import Violation
from django.contrib.gis.geos import Point

from datetime import datetime


def convert_date(date_str: str, input_format: str = "%m/%d/%Y", output_format: str = "%Y-%m-%d"):
    """
    Convert a date string from one format to another.

    :param date_str: The date string to convert.
    :param input_format: The format of the input date string.
    :param output_format: The desired format for the output date string.
    :return: The converted date string.
    """
    # Check for empty or whitespace-only strings
    if not date_str.strip():
        return None
    try:
        return datetime.strptime(date_str, input_format).strftime(output_format)
    except ValueError as e:
        raise ValueError(f"Error converting date: {e}")


class Command(BaseCommand):
    # ref: https://docs.djangoproject.com/en/dev/howto/custom-management-commands/

    help = "Ingest raw violations from a .csv file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help="Path to the .csv file",
            default="data/violations_20250421_hp.csv",
        )

    def handle(self, *args, **kwargs):
        with open(kwargs["file"]) as f:
            data = csv.DictReader(f)
            for idx, row in enumerate(data):
                try:
                    Violation.objects.create(
                        violation_id=row["ID"],
                        violation_last_modified_date=convert_date(
                            row["VIOLATION LAST MODIFIED DATE"]
                        ),
                        violation_date=convert_date(row["VIOLATION DATE"]),
                        violation_code=row["VIOLATION CODE"],
                        violation_status=row["VIOLATION STATUS"],
                        violation_status_date=convert_date(row["VIOLATION STATUS DATE"]),
                        violation_description=row["VIOLATION DESCRIPTION"],
                        violation_location=row["VIOLATION LOCATION"],
                        violation_inspector_comments=row["VIOLATION INSPECTOR COMMENTS"],
                        violation_ordinance=row["VIOLATION ORDINANCE"],
                        inspector_id=row["INSPECTOR ID"],
                        inspection_number=row["INSPECTION NUMBER"],
                        inspection_status=row["INSPECTION STATUS"],
                        inspection_waived=row["INSPECTION WAIVED"],
                        inspection_category=row["INSPECTION CATEGORY"],
                        department_bureau=row["DEPARTMENT BUREAU"],
                        address=row["ADDRESS"],
                        street_number=row["STREET NUMBER"],
                        street_direction=row["STREET DIRECTION"],
                        street_name=row["STREET NAME"],
                        street_type=row["STREET TYPE"],
                        property_group=row["PROPERTY GROUP"],
                        ssa=row["SSA"],
                        latitude=row["LATITUDE"],
                        longitude=row["LONGITUDE"],
                        location=Point(float(row["LATITUDE"]), float(row["LONGITUDE"])),  # FIXME
                    )
                except IntegrityError:
                    continue
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Errorprocessing row {idx}: {e}\n{row}"))
        self.stdout.write(self.style.SUCCESS("Successfully imported raw violations"))
