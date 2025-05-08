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
from apt_app.views import home, about, fetch_all_data
from apt_app.views_v2.groceries import fetch_groceries
from django.conf import settings
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path("", home, name="home"),
    path("about", about, name="about"),
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    path("fetch_all_data/", fetch_all_data, name="fetch_all_data"),
  path("fetch_groceries/", fetch_groceries, name="fetch_groceries"),]

if settings.DEBUG and not settings.IS_TESTING:
    urlpatterns += debug_toolbar_urls()
