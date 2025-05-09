# from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from apt_app.views_functions.function_fetch_all_data import fetching_all_data

# Create your views here.


def home(request):
    return HttpResponse("Server is running", status=200)


@api_view(["POST"])
def fetch_all_data(request):
    address = request.data.get("address")
    json_response = fetching_all_data(address)
    return json_response
