from django.shortcuts import render
from django.http import HttpResponse
from apt_app.models import SavedProperty


def _saved_properties(request):
    """View for the user to see all their saved properties"""

    # This endpoint only works if the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("Authentication required", status=401)

    # Checking if the user has any saved properties
    saved_properties = SavedProperty.objects.filter(
        user=request.user, is_deleted=False
    ).select_related("property_obj")

    return render(
        request,
        "saved_properties.html",
        {"saved_properties": saved_properties},
    )
