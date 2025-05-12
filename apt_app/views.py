import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from apt_app.views_functions.function_fetch_all_data import fetching_all_data


def home(request):
    # todo
    print(request.user)
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


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


@csrf_exempt
def fetch_all_data(request):
    address = request.POST.get("address")
    json_response = fetching_all_data(address)
    return json_response
