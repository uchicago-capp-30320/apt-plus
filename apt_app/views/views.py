import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from .fetch_inspections import _fetch_inspection_summaries


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


@require_GET
def fetch_inspections(request):
    address = request.GET.get("address", "")
    return _fetch_inspection_summaries(address)
