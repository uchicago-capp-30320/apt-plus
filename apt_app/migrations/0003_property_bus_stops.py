# Generated by Django 5.2 on 2025-05-08 00:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("apt_app", "0002_amenity_crime_property_inspection_favoriteproperty_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="property",
            name="bus_stops",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
