# Generated by Django 5.2.1 on 2025-05-26 06:59

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('apt_app', '0015_rename_property_savedproperty_property_obj_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='amenity',
            constraint=models.UniqueConstraint(fields=('address', 'type'), name='unique_address_type'),
        ),
    ]