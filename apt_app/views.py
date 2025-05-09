# from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from apt_app.views_functions.function_fetch_all_data import fetching_all_data

# Create your views here


def home(request):
    return HttpResponse("Server is running", status=200)


@csrf_exempt
def fetch_all_data(request):
    address = request.POST.get("address")
    json_response = fetching_all_data(address)
    return json_response
