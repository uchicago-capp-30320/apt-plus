import re
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from apt_app.models import SavedProperty


def _delete_property(request):
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

        # Handling the case where the property is not found
        if not saved_property:
            return HttpResponse("Saved property not found", status=404)

        # Soft deleting the property
        saved_property.soft_delete()

        proper_address = property_address.title()
        proper_address = re.sub(r"\b(Il)\b", "IL", proper_address)

        # Return template to replace the button
        return render(
            request,
            "snippets/delete_property_response.html",
            {"property_address": proper_address},
        )

    return HttpResponse("Method not allowed", status=405)
