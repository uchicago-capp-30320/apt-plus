from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from apt_app.models import SavedProperty


@csrf_exempt
def _update_property(request):
    """Handle saving property details."""

    # Update is only allowed for authenticated users
    if not request.user.is_authenticated:
        return HttpResponse("Authentication required", status=401)

    if request.method == "POST":
        # Get form data
        property_address = request.POST.get("property_address", "")
        property_address_upper_case = property_address.upper()
        property_custom_name = request.POST.get("property_custom_name", "")
        property_notes = request.POST.get("property_notes", "")
        property_rent = request.POST.get("property_rent", "")

        # Rent is an integer field, cannot store empty strings
        if property_rent == "":
            property_rent = None

        # Getting the saved property ID
        matching_saved_property = SavedProperty.objects.filter(
            user=request.user, address=property_address_upper_case
        ).first()

        if matching_saved_property:
            matching_saved_property.custom_name = property_custom_name
            matching_saved_property.remarks = property_notes
            matching_saved_property.rent_price = property_rent
            matching_saved_property.save()
        else:
            return HttpResponse("Matching saved property not found", status=404)

        # Return HTML that replaces just the form container
        return render(
            request, "snippets/details_saved.html", {"property_address": property_address}
        )

    return HttpResponse("Method not allowed", status=405)
