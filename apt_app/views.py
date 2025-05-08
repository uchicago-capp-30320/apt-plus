import json
from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def fetch_all_data(request):
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
