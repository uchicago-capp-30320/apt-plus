# Generated by Django 5.2.1 on 2025-05-29 02:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apt_app', '0017_remove_favoriteproperty_property_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspectionsummary',
            name='property',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='apt_app.property'),
        ),
    ]
