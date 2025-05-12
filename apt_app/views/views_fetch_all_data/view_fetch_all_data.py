from .function_fetch_all_data import fetching_all_data
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def fetch_all_data(request):
    address = request.POST.get("address")
    json_response = fetching_all_data(address)
    return json_response
