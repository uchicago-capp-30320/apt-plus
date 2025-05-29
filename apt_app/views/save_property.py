import re
from django.shortcuts import render
from django.http import HttpResponse
from apt_app.models import Property, SavedProperty


def _save_property(request):
    """Core logic for saving a property."""
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    # Get the address from the request
    property_address = request.POST.get("propertyAddress", "Unknown Address")

    # Check authentication
    # If the user is not authenticated, and still click on the save button,
    # we throw a message asking them to sign in. Once they sign in, they are
    # redirected to the result page.
    if not request.user.is_authenticated:
        # Store the address for post-login redirection
        request.session["pending_property_address"] = property_address

        # Return a specific HTML snippet for unauthenticated users
        login_url = "/accounts/login/?next=/handle_post_login/"
        return render(
            request,
            "snippets/save_property_login_required.html",
            {"login_url": login_url, "property_address": property_address},
        )

    # Title-case the string
    # This is passed to the template for displaying to the user
    proper_address = property_address.title()
    proper_address = re.sub(r"\b(Il)\b", "IL", proper_address)

    # Find the property in the Property table
    # Whenever querying the database, defaulting to always user `upper()` just
    # in case
    matching_property = Property.objects.filter(address=property_address.upper()).first()

    if not matching_property:
        print("Could not find property in the Property table")
        return HttpResponse("Could not find property in the Property table", status=400)

    # Check if the property is already present in saved_property
    property_in_savedproperty = SavedProperty.objects.filter(
        user=request.user, address=property_address.upper()
    ).first()

    # Handle existing or deleted properties
    # If property exists but happens to be deleted, we will restore it
    if property_in_savedproperty:
        if property_in_savedproperty.is_deleted:
            property_in_savedproperty.restore()
        else:
            pass
    else:
        # Since the property has not previously been saved, we will create a
        # new instance and save it
        saved_property = SavedProperty(
            user=request.user,
            property_obj=matching_property,
            address=property_address.upper(),
        )
        saved_property.save()

    # Return template to replace the button
    return render(request, "snippets/save_property.html", {"property_address": proper_address})
