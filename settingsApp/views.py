from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from .models import SchoolSettings, Subscription


def is_admin(user):
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(is_admin)
def school_settings(request):
    """
    School Settings page.
    """

    settings_obj, created = SchoolSettings.objects.get_or_create(
        pk=1,
        defaults={
            "school_name": "Green Apple Academy",
            "academic_year": "2026",
            "current_term": "Term 1",
        },
    )

    subscription, created = Subscription.objects.get_or_create(
        school=settings_obj
    )

    if request.method == "POST":

        settings_obj.school_name = request.POST.get(
            "school_name",
            settings_obj.school_name,
        )

        settings_obj.motto = request.POST.get(
            "motto",
            settings_obj.motto,
        )

        settings_obj.email = request.POST.get(
            "email",
            settings_obj.email,
        )

        settings_obj.phone = request.POST.get(
            "phone",
            settings_obj.phone,
        )

        settings_obj.website = request.POST.get(
            "website",
            settings_obj.website,
        )

        settings_obj.address = request.POST.get(
            "address",
            settings_obj.address,
        )

        settings_obj.city = request.POST.get(
            "city",
            settings_obj.city,
        )

        settings_obj.country = request.POST.get(
            "country",
            settings_obj.country,
        )

        settings_obj.currency = request.POST.get(
            "currency",
            settings_obj.currency,
        )

        settings_obj.academic_year = request.POST.get(
            "academic_year",
            settings_obj.academic_year,
        )

        settings_obj.current_term = request.POST.get(
            "current_term",
            settings_obj.current_term,
        )

        settings_obj.reception_enabled = (
            request.POST.get("reception_enabled") == "on"
        )

        settings_obj.pre_grade_enabled = (
            request.POST.get("pre_grade_enabled") == "on"
        )

        if request.FILES.get("logo"):
            settings_obj.logo = request.FILES["logo"]

        settings_obj.save()

        messages.success(
            request,
            "School settings updated successfully.",
        )

        return redirect("school_settings")

    context = {
        "settings": settings_obj,
        "subscription": subscription,
    }

    return render(
        request,
        "settingsApp/settings.html",
        context,
    )


@login_required
@user_passes_test(is_admin)
def subscription_details(request):

    settings_obj = get_object_or_404(
        SchoolSettings,
        pk=1,
    )

    subscription = get_object_or_404(
        Subscription,
        school=settings_obj,
    )

    context = {
        "settings": settings_obj,
        "subscription": subscription,
    }

    return render(
        request,
        "settingsApp/subscription.html",
        context,
    )