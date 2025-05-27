import os
import csv
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from apt_app.models import Violation
from django.contrib.gis.geos import Point
from datetime import datetime
from scripts import inspections_utils as iu


class Command(BaseCommand):
    # ref: https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/

    help = "Ingest raw violations from a .csv file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help="Path to the .csv file",
            default="data/violations_20250421_hp.csv",
        )

        parser.add_argument(
            "--stream", action="store_true", help="Whether to ingest in stream or batch (default)"
        )

    def handle(self, *args, **kwargs):
        if kwargs["stream"]:
            self.stream_ingest(*args, **kwargs)
        else:
            self.batch_ingest(*args, **kwargs)

    def batch_ingest(self, *args, **kwargs):
        try:
            df_in = pd.read_csv(kwargs["file"])
            objs: list = [iu.create_one_violation_object(row) for _, row in df_in.iterrows()]
            Violation.objects.bulk_create(objs, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS("Successfully imported raw violations"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing raw violations: {e}"))

    def stream_ingest(self, *args, **kwargs):
        with open(kwargs["file"]) as f:
            data = csv.DictReader(f)
            for idx, row in enumerate(data):
                try:
                    obj = iu.create_one_violation_object(row)
                    obj.save()
                except IntegrityError:
                    continue
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Errorprocessing row {idx}: {e}\n{row}"))
        self.stdout.write(self.style.SUCCESS("Successfully imported raw violations"))
