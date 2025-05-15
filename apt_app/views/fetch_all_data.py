import os
import sys
import censusgeocode as cg
import json
from dotenv import load_dotenv
import django  # noqa: E402
from django.core.exceptions import ValidationError  # noqa: E402
from django.http import JsonResponse  # noqa: E402

# Import model Property
from apt_app.models import Property  # noqa: E402
from config import load_constants

CONSTANTS = load_constants()
NORTH = CONSTANTS["HP_BOUNDS"]["north"]
SOUTH = CONSTANTS["HP_BOUNDS"]["south"]
EAST = CONSTANTS["HP_BOUNDS"]["east"]
WEST = CONSTANTS["HP_BOUNDS"]["west"]


# sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
# Load environment variables
# load_dotenv()

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


def _fetch_all_data(user_address):
    """
    Function that takes the user_address string, and does the following:
    (i) Check that user_address is matched with an address from censusgeocode
    (ii) Get its coordinates and check that the address is inside Hyde Park
    (iii) Add the address to the Django database if it didn't exist previously
    (iv) Returns Response with JSON with cleaned_address, property_id, coordinates,
    and original user_address
    """
    # See if some address was provided by the user
    if not user_address or not isinstance(user_address, str):
        return JsonResponse({"Error": "Address is required."}, status=400)

    # Try to match the address using censusgeocode
    try:
        result = cg.address(user_address, city="Chicago", state="IL")
    except Exception as e:
        return JsonResponse(
            {"Error": f"Censusgeocode service error: {e}"},
            status=500,
        )

    # Check if address is matched to any address
    ## NOTE: Censusgeocode returns an empty list when the address is not matched
    if result == []:
        return JsonResponse(
            {"Error": "No matched address found in the database."},
            status=400,
        )

    # Address was matched, get the matched address and its coordinates
    matched_address = result[0].get("matchedAddress")
    longitude = result[0].get("coordinates", {}).get("x")
    latitude = result[0].get("coordinates", {}).get("y")

    # Check if address is within the coordinates defined for "Hyde Park"
    north_limit_latitude = NORTH
    south_limit_latitude = SOUTH
    east_limit_longitude = EAST
    west_limit_longitude = WEST
    if not (east_limit_longitude <= longitude <= west_limit_longitude) or not (
        south_limit_latitude <= latitude <= north_limit_latitude
    ):
        return JsonResponse(
            {"Error": "Address is not inside the area defined for the project."},
            status=400,
        )

    # Save address in django (if necessary) and get its id
    property_id = save_property_in_django(matched_address, latitude, longitude)

    # 3. Return result
    return JsonResponse(
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
        status=200,
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
    except Exception as e:
        raise ValueError(f"{property.address} could not be uploaded: {e}")

    return property.id


if __name__ == "__main__":
    # Trial with example of user address, with prints to check that it is working
    user_address_example = "5496 S Hyde Park Blvd"
    response_example = _fetch_all_data(user_address_example)
    print(f"Status Code: {response_example.status_code}")
    body_dict = json.loads(response_example.content.decode())
    print(f"Response Data: {body_dict}")
    print(f"Cleaned Address: {body_dict['cleaned_address']}")
