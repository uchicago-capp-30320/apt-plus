import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

import censusgeocode as cg
import django
from dotenv import load_dotenv
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Load environment variables
load_dotenv()

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import model
from apt_app.models import Property  # must be after django.setup()


def fetch_all_data(user_address):
    """
    Auxiliar function that takes the user_address string, and do the following:
    (i) Check that is matched with an address from censusgeocode
    (ii) Get the coordinates and check that the address is inside Hyde Park
    (iii) Add the address to the Django database if it didn't exist previously
    (iv) Returns multiple stuff
    """
    # See if some address was provided by the user
    if not user_address or not isinstance(user_address, str):
        return Response({"Error": "Address is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Try to match the address using censusgeocode
    try:
        result = cg.address(user_address, city="Chicago", state="IL")
    except Exception as e:
        return Response(
            {"Error": f"Censusgeocode service error: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Check if address is matched to any address
    ## NOTE: Censusgeocode returns an empty list when the address is not matched
    if result == []:
        return Response(
            {"Error": "No matched address found in the database."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Address was matched, get the matched address and its coordinates
    matched_address = result[0].get("matchedAddress")
    longitude = result[0].get("coordinates", {}).get("x")
    latitude = result[0].get("coordinates", {}).get("y")

    # Check if address is within the coordinates defined for "Hyde Park"
    north_limit_latitude = 41.809647
    south_limit_latitude = 41.780482
    east_limit_longitude = -87.615877
    west_limit_longitude = -87.579056
    if not (east_limit_longitude <= longitude <= west_limit_longitude) or not (
        south_limit_latitude <= latitude <= north_limit_latitude
    ):
        return Response(
            {"Error": "Address is not inside the area defined for the project."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Save address in django (if necessary) and get its id
    property_id = save_property_in_django(matched_address, latitude, longitude)

    # 3. Return result
    return Response(
        {
            "cleaned_address": matched_address,
            "property_id": property_id,
            "address_geojson": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                longitude,
                                latitude,
                            ],
                        },
                        "properties": {
                            "label": user_address  # Original address provided by user
                        },
                    }
                ],
            },
        },
        status=status.HTTP_200_OK,
    )


def save_property_in_django(address_input, latitude, longitude):
    """
    Helper function that generates a TransitStop instance and saves it.
    """
    property = Property()

    # Check if property already exists in django
    try:
        property_exists = Property.objects.filter(address=address_input).get()
    except Property.DoesNotExist:
        property_exists = False

    # if exists, return the id and don't continue with function
    if property_exists:
        print(f"Property already in database, ID: {property_exists.id}")
        return property_exists.id

    # Name
    property.address = address_input

    # Location
    try:
        property.setup_location(latitude, longitude)
    except ValidationError as e:
        raise ValueError(f"Invalid location: {e}")

    # Save it in django
    try:
        property.save()
        print(f"Property saved with ID: {property.id}")
    except Exception as e:
        raise ValueError(f"{property.address} could not be uploaded: {e}")

    return property.id


if __name__ == "__main__":
    # Trial with example of user address, with prints to check that it is working
    user_address_example = "5496 S Hyde Park Blvd"
    response_example = fetch_all_data(user_address_example)
    print(f"Status Code: {response_example.status_code}")
    print(f"Response Data: {response_example.data}")
