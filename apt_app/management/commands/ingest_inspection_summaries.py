import os
import json
from django.core.management.base import BaseCommand, CommandError
from apt_app.models import InspectionSummary


class Command(BaseCommand):
    # ref: https://docs.djangoproject.com/en/dev/howto/custom-management-commands/

    help = "Ingest inspection summaries from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help="Path to the JSON file",
            default="data/inspection_summaries.json",
        )

    def handle(self, *args, **kwargs):
        with open(kwargs["file"]) as f:
            data = json.load(f)
            for address, json_object in data.items():
                InspectionSummary.objects.create(
                    # property_id=None,
                    address=address,
                    summary=json_object,
                )
        self.stdout.write(self.style.SUCCESS("Successfully imported inspection summaries"))
