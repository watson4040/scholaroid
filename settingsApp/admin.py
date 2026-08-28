from django.contrib import admin
from .models import SchoolSettings, Subscription


@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "school_name",
        "academic_year",
        "current_term",
        "country",
        "updated_at",
    )

    search_fields = (
        "school_name",
        "email",
        "phone",
    )

    list_per_page = 20

    fieldsets = (
        (
            "School Information",
            {
                "fields": (
                    "school_name",
                    "motto",
                    "logo",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "email",
                    "phone",
                    "website",
                    "address",
                    "city",
                    "country",
                )
            },
        ),
        (
            "Academic Settings",
            {
                "fields": (
                    "academic_year",
                    "current_term",
                    "currency",
                    "reception_enabled",
                    "pre_grade_enabled",
                )
            },
        ),
        (
            "School Hours",
            {
                "fields": (
                    "school_open",
                    "school_close",
                )
            },
        ),
        (
            "Branding",
            {
                "fields": (
                    "primary_color",
                    "secondary_color",
                )
            },
        ),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "school",
        "plan",
        "status",
        "start_date",
        "expiry_date",
        "days_remaining",
    )

    list_filter = (
        "plan",
        "status",
    )

    search_fields = (
        "school__school_name",
    )

    readonly_fields = (
        "days_remaining",
        "is_expired",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Subscription",
            {
                "fields": (
                    "school",
                    "plan",
                    "status",
                )
            },
        ),
        (
            "License",
            {
                "fields": (
                    "start_date",
                    "expiry_date",
                    "days_remaining",
                    "is_expired",
                )
            },
        ),
        (
            "Limits",
            {
                "fields": (
                    "max_users",
                    "max_pupils",
                )
            },
        ),
        (
            "Notes",
            {
                "fields": (
                    "notes",
                )
            },
        ),
        (
            "System",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )