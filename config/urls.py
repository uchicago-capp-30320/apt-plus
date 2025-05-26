"""
URL configuration for apt_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from apt_app.views.views import (
    home,
    about,
    fetch_all_data,
    fetch_bus_stops,
    fetch_groceries,
    fetch_inspections,
    fetch_bus_routes,
    save_property,
    update_property,
    handle_post_login,
    check_property_status,
    delete_property,
    saved_properties,
)
from django.conf import settings
from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", home, name="home"),
    path("about", about, name="about"),
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    path("fetch_bus_stops/", fetch_bus_stops, name="fetch_bus_stops"),
    path("fetch_all_data/", fetch_all_data, name="fetch_all_data"),
    path("fetch_groceries/", fetch_groceries, name="fetch_groceries"),
    path(
        "fetch_inspections/",
        fetch_inspections,
        name="fetch_inspection_summaries",
    ),
    path("fetch_bus_routes/", fetch_bus_routes, name="fetch_bus_routes"),
    path("save_property/", save_property, name="save_property"),
    path("update_property/", update_property, name="update_property"),
    path("handle_post_login/", handle_post_login, name="handle_post_login"),
    path("check_property_status/", check_property_status, name="check_property_status"),
    path("delete_property/", delete_property, name="delete_property"),
    path("saved_properties/", save_property, name="saved_properties"),
]

if settings.DEBUG and not settings.IS_TESTING:
    urlpatterns += debug_toolbar_urls()
