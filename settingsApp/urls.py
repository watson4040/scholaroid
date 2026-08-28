from django.urls import path
from . import views

app_name = "settingsApp"

urlpatterns = [
    path(
        "",
        views.school_settings,
        name="school_settings",
    ),
    path(
        "subscription/",
        views.subscription_details,
        name="subscription_details",
    ),
]