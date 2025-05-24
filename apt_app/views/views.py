import json
import re
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceRatio
from django.shortcuts import redirect
from apt_app.models import TransitStop, Property
from django.contrib.gis.db.models.functions import Distance as DistanceFunction
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from .fetch_all_data import _fetch_all_data
from .fetch_groceries import _fetch_groceries
from .fetch_bus_stops import _fetch_bus_stops
from .fetch_inspections import _fetch_inspection_summaries
from apt_app.models import SavedProperty


def home(request):
    # TODO: remove print debugging
    print(f"Current user: {request.user}")
    print(f"Authentication status: {request.user.is_authenticated}")
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


@csrf_exempt
@require_GET
def fetch_all_data(request):
    address = request.GET.get("address")
    return _fetch_all_data(address)


@require_GET
def fetch_groceries(request):
    # extract parameters from request
    geocode = request.GET.get("geocode")
    walking_time = int(request.GET.get("walking_time", 5))
    return _fetch_groceries(geocode, walking_time)


@require_GET
def fetch_bus_stops(request):
    geocode = request.GET.get("geocode")
    walking_time = int(request.GET.get("walking_time", 5))  # default 5 min
    property_id = request.GET.get("property_id")
    return _fetch_bus_stops(geocode, property_id, walking_time)


@require_GET
def fetch_inspections(request):
    address = request.GET.get("address", "")
    return _fetch_inspection_summaries(address)


# TODO: this should be moved elsewhere since it is a hard-coded mock
# -- maybe should be in tests but not sure
def fetch_all_data_mock(request):
    address = request.GET.get("address", "")

    print(address)

    # Generating a sample geojson response with a point lying inside
    # Hyde Park, Chicago
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-87.591848, 41.801696]},
                "properties": {"name": "Hyde Park, Chicago"},
            }
        ],
    }
    # Convert the dictionary to a JSON string before returning
    return HttpResponse(json.dumps(geojson), content_type="application/json")


def save_property(request):
    """Save a property and return HTML to replace the button."""

    # TODO:
    # Better error handling
    # Should the saved property ID also be sent to the template?

    print("Save property endpoint triggered")

    # Get the address from the request
    property_address = request.GET.get("propertyAddress", "Unknown Address")

    # Checking if the user is signed in
    # If they are not, then we offer them an option to log in
    if not request.user.is_authenticated:
        request.session["pending_property_address"] = property_address

        # Creating the login URL
        login_url = "/accounts/login/?next=/handle_post_login/"

        return render(
            request, "snippets/save_property_login_required.html", {"login_url": login_url}
        )

    # Title-case the string
    proper_address = property_address.title()

    # Regular expression to correct common uppercase abbreviations (like state codes, "IL" here)
    proper_address = re.sub(r"\b(Il)\b", "IL", proper_address)

    # Saving the property to the database
    # Need to also check if the property doesn't already exist in the user's
    # saved properties

    # First need to query the database to get the the property ID
    matching_property = Property.objects.filter(address=property_address).first()

    if matching_property:
        print(f"ID: {matching_property.id}")
        print(f"Address: {matching_property.address}")
        print(f"Location: {matching_property.location}")
        print(f"Created At: {matching_property.created_at}")
        print(f"Bus Stops: {matching_property.bus_stops}")
    else:
        print("No matching property found.")

    if not matching_property:
        return HttpResponse("Could not find property in the Property table", status=400)

    # Check if the property is already present in saved_property
    # There can be two cases:
    # 1. The property is not present in the SavedProperty table at all
    # 2. The property is present, but is currently deleted

    property_in_savedproperty = SavedProperty.objects.filter(
        user=request.user, address=property_address
    ).first()

    if property_in_savedproperty:
        # There is a match
        # The user already has a property with this name saved
        # We will not create a new record
        # Just ensure that the is_deleted status is False
        property_in_savedproperty.is_deleted = False
        property_in_savedproperty.save()
    elif not property_in_savedproperty:
        # The propert does not exist in the table, will be created
        saved_property = SavedProperty(
            user=request.user,
            property=matching_property,
            address=property_address,
        )

        saved_property.save()

    # Return template to replace the button
    return render(request, "snippets/save_property.html", {"property_address": proper_address})


def handle_post_login(request):
    """Handle users returning after login with a pending property view."""
    if request.user.is_authenticated:
        # Check for pending address in session
        pending_address = request.session.get("pending_property_address")

        if pending_address:
            # Clear from session
            del request.session["pending_property_address"]

            # Store in a variable we'll pass to the template
            return render(request, "return_to_property.html", {"property_address": pending_address})

    # Default fallback - just go to homepage
    return redirect("/")


@csrf_exempt
def update_property(request):
    """Handle saving property details."""
    if request.method == "POST":
        # Get form data
        property_address = request.POST.get("property_address", "")
        property_address_upper_case = property_address.upper()
        property_custom_name = request.POST.get("property_custom_name", "")
        property_notes = request.POST.get("property_notes", "")
        property_rent = request.POST.get("property_rent", "")

        if property_rent == "":
            property_rent = None

        print(f"Updating property: {property_address}")
        print(f"Upper case property address: {property_address.upper()}")
        print(f"Custom name: {property_custom_name}")
        print(f"Notes: {property_notes}")
        print(f"Rent: {property_rent}")

        # Need to add database logic

        # Getting the saved property ID
        matching_saved_property = SavedProperty.objects.filter(
            user=request.user, address=property_address_upper_case
        ).first()

        if matching_saved_property:
            print(f"ID: {matching_saved_property.id}")
            print(f"Address: {matching_saved_property.address}")
            print(f"User: {matching_saved_property.user}")
        else:
            print("No matching property found.")

        if matching_saved_property:
            matching_saved_property.custom_name = property_custom_name
            matching_saved_property.remarks = property_notes
            matching_saved_property.rent_price = property_rent

            matching_saved_property.save()

        # Return HTML that replaces just the form container
        return render(
            request, "snippets/details_saved.html", {"property_address": property_address}
        )

    return HttpResponse("Method not allowed", status=405)


@csrf_exempt
def delete_property(request):
    """Handle soft delete property from the SavedProperty table"""

    # Delete can happen only if the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("Authentication required", status=401)

    if request.method == "POST":
        property_address = request.POST.get("property_address", "")

        if not property_address:
            return HttpResponse("Property address is required", status=400)

        # Finding the property
        property_address_upper_case = property_address.upper()
        saved_property = SavedProperty.objects.filter(
            user=request.user, address=property_address_upper_case, is_deleted=False
        ).first()

        # Handling the case where the error is not found
        if not saved_property:
            return HttpResponse("Saved property not found", status=404)

        # Soft deleting the property
        saved_property.soft_delete()

        html_response = f"""
        <div id="save-button-container" class="mb-4 slide-it">
            <div class="notification is-success">
                <strong>{property_address}</strong> has been removed from your list.
            </div>
            <button class="button is-rounded has-text-white has-background-black mt-2"
                    id="save-button"
                    hx-get="/save_property/"
                    hx-vals='js:{{propertyAddress: "{property_address}"}}'
                    hx-target="#save-button-container"
                    hx-trigger="click"
                    hx-swap="outerHTML transition:true">
                Save to my list
            </button>
        </div>
        """

        return HttpResponse(html_response)

    return HttpResponse("Method not allowed", status=405)


def check_property_status(request):
    """Helper view to check if the property is saved"""
    if not request.user.is_authenticated:
        return JsonResponse({"is_saved": False, "message": "User not authenticated"})

    # Getting the property address from the request
    property_address = request.GET.get("property_address", "")

    if not property_address:
        return JsonResponse({"error": "Address required"}, status=400)

    # Checking if the property exists in the user's saved properties
    is_saved = SavedProperty.objects.filter(
        user=request.user, address=property_address.upper(), is_deleted=False
    ).exists()

    return JsonResponse({"is_saved": is_saved, "property_address": property_address})


# save property needs to check for delete status as well
