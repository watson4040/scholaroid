from django.contrib import admin

from .models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):

    # Columns shown in admin list page
    list_display = (
        "name",
        "email",
        "subscription_plan",
        "active",
        "created_at",
    )


    # Filters on the right side
    list_filter = (
        "subscription_plan",
        "active",
        "country",
    )


    # Search box
    search_fields = (
        "name",
        "email",
        "phone",
    )


    # Fields that cannot be edited manually
    readonly_fields = (
        "created_at",
        "updated_at",
    )


    # Better form layout
    fieldsets = (

        (
            "School Information",
            {
                "fields": (
                    "name",
                    "email",
                    "phone",
                    "address",
                    "city",
                    "country",
                )
            },
        ),


        (
            "Subscription",
            {
                "fields": (
                    "subscription_plan",
                    "active",
                )
            },
        ),


        (
            "Paystack Integration",
            {
                "fields": (
                    "paystack_subaccount_code",
                )
            },
        ),


        (
            "Ownership",
            {
                "fields": (
                    "owner",
                )
            },
        ),


        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),

    )