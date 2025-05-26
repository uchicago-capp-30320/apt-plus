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


t = [
    {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-87.59625, 41.795037]},
        "properties": {
            "routes": ["171", "55"],
            "stop_id": 15752,
            "stop_name": "55th Street & Woodlawn",
            "distance_min": 5,
        },
    },
    {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-87.598125, 41.794853]},
        "properties": {
            "routes": ["171"],
            "stop_id": 15816,
            "stop_name": "University & 55th Street",
            "distance_min": 4,
        },
    },
    {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-87.596393, 41.795188]},
        "properties": {
            "routes": ["171", "55"],
            "stop_id": 10572,
            "stop_name": "55th Street & Woodlawn",
            "distance_min": 4,
        },
    },
    {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-87.596634, 41.799847]},
        "properties": {
            "routes": ["172"],
            "stop_id": 14039,
            "stop_name": "Woodlawn & 53rd Street",
            "distance_min": 4,
        },
    },
    {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-87.596488, 41.794902]},
        "properties": {
            "routes": ["172"],
            "stop_id": 14043,
            "stop_name": "Woodlawn & 55th Street",
            "distance_min": 5,
        },
    },
    {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-87.601305, 41.799297]},
        "properties": {
            "routes": ["172"],
            "stop_id": 14886,
            "stop_name": "Ellis & 53rd Street",
            "distance_min": 5,
        },
    },
    {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-87.596657, 41.799595]},
        "properties": {
            "routes": ["172"],
            "stop_id": 14036,
            "stop_name": "Woodlawn & 53rd Street",
            "distance_min": 4,
        },
    },
    {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-87.59768, 41.795013]},
        "properties": {
            "routes": ["55"],
            "stop_id": 18018,
            "stop_name": "55th Street & University",
            "distance_min": 4,
        },
    },
    {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-87.598713, 41.7951]},
        "properties": {
            "routes": ["55"],
            "stop_id": 15753,
            "stop_name": "55th Street & University",
            "distance_min": 4,
        },
    },
]
