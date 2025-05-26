from django.http import JsonResponse
from apt_app.models import SavedProperty


def _check_property_status(request):
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
