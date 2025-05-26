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

# Get coordinates related to Hyde Park boundaries
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


def _fetch_all_data(user_address) -> JsonResponse:
    """
    Function that takes the user_address string, and does the following:
    (i) Check that user_address is matched with an address from censusgeocode
    and get its coordinates
    (ii) Check if the address is inside Hyde Park or Chicago
    (iii) Add the address to the Django database if it didn't exist previously
    (iv) Returns Response with JSON with cleaned_address, property_id, coordinates,
    and original user_address
    """
    # See if some address was provided by the user
    if not user_address or not isinstance(user_address, str):
        return JsonResponse({"Error": "Address is required."}, status=400)

    # Try to match the address in Chicago to get a matched address and its coordinates
    return_of_match_address = match_address_in_chicago(user_address)
    # If there was a known error in the function, return that JsonResponse
    if isinstance(return_of_match_address, JsonResponse):
        return return_of_match_address
    else:
        matched_address, longitude, latitude = return_of_match_address

    # Check if address is within the coordinates defined for "Hyde Park"
    inside_hyde_park_boolean = coordinates_in_hyde_park(latitude, longitude)
    if inside_hyde_park_boolean:
        inside_hyde_park_message = "Address is inside the perimeter of Hyde Park"
    else:
        inside_hyde_park_message = (
            "Address is not inside the perimeter of the Hyde Park area, "
            + "so some functionalities of the application will not work, such as"
            + " inspections data or shuttle buses."
        )

    # Save address in django (if necessary) and get its id
    property_id = save_property_in_django(matched_address, latitude, longitude)

    # Return result
    return JsonResponse(
        {
            "cleaned_address": matched_address,
            "property_id": property_id,
            "has_data_inside_hyde_park": inside_hyde_park_boolean,
            "notes": inside_hyde_park_message,
            "address_geojson": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                latitude,
                                longitude,
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


def match_address_in_chicago(address_input):
    """
    Helper function that takes a raw address as an input and returns the
    matched address, its coordinates, and if its in Chicago.

    Inputs:
        - address_input: Raw address.

    Returns (tuple): tuple with four variables:
        - matched_address (str): address which the raw address was matched with
        - longitude (float): longitude of the matched address
        - latitude (float): latitude of the matched address
        - urban_area (bool): urban area is Chicago or not
    """
    # Try to match the address using censusgeocode
    try:
        result = cg.address(address_input, city="Chicago", state="IL")
    except Exception as e:
        return JsonResponse(
            {"Error": f"Censusgeocode service error: {e}"},
            status=500,
        )

    # Check if address is matched to any address
    ## NOTE: Censusgeocode returns an empty list when the address is not matched
    if result == []:
        return JsonResponse(
            {"Error": "No matched address found in Chicago."},
            status=400,
        )

    # Address was matched, get the matched address, urban area, and its coordinates
    matched_address = result[0].get("matchedAddress")
    longitude = result[0].get("coordinates", {}).get("x")
    latitude = result[0].get("coordinates", {}).get("y")
    urban_area = result[0]["geographies"]["Urban Areas"][0]["BASENAME"]

    # If address not in chicago, return error message
    if not urban_area == "Chicago, IL--IN":
        return JsonResponse(
            {"Error": "Address is not inside Chicago, the area defined for the project."},
            status=400,
        )

    return matched_address, longitude, latitude


def coordinates_in_hyde_park(latitude, longitude):
    """
    Check if an area is inside the boundaries defined for Hyde Park. Returns
    a string message with the result.
    """
    north_limit_latitude = NORTH
    south_limit_latitude = SOUTH
    east_limit_longitude = EAST
    west_limit_longitude = WEST
    if (west_limit_longitude <= longitude <= east_limit_longitude) and (
        south_limit_latitude <= latitude <= north_limit_latitude
    ):
        return True
    else:
        return False


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
