from django.db import models
from django.conf import settings


class School(models.Model):

    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


    PLAN_CHOICES = [

        (BASIC, "Basic"),

        (PROFESSIONAL, "Professional"),

        (ENTERPRISE, "Enterprise"),

    ]


    # =====================================
    # SCHOOL PROFILE
    # =====================================

    name = models.CharField(
        max_length=200
    )


    email = models.EmailField(
        unique=True
    )


    phone = models.CharField(
        max_length=30,
        blank=True
    )


    address = models.TextField(
        blank=True
    )


    city = models.CharField(
        max_length=100,
        blank=True
    )


    country = models.CharField(
        max_length=100,
        default="Zambia"
    )


    # =====================================
    # OWNER
    # =====================================

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schools_owned"
    )


    # =====================================
    # SUBSCRIPTION
    # =====================================

    subscription_plan = models.CharField(
        max_length=30,
        choices=PLAN_CHOICES,
        default=BASIC
    )


    subscription_active = models.BooleanField(
        default=False
    )


    subscription_expiry = models.DateField(
        null=True,
        blank=True
    )


    # =====================================
    # PAYSTACK SPLIT PAYMENT
    # =====================================

    paystack_subaccount_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )


    paystack_recipient_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )


    # Nexor Labs commission
    platform_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text="Percentage retained by Nexor Labs"
    )


    paystack_verified = models.BooleanField(
        default=False
    )


    # =====================================
    # STATUS
    # =====================================

    active = models.BooleanField(
        default=True
    )


    # =====================================
    # TIMESTAMPS
    # =====================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    class Meta:

        ordering = [
            "name"
        ]


        verbose_name = "School"


        verbose_name_plural = "Schools"



    def __str__(self):

        return self.name



    def school_fee_split(self):

        """
        Returns school percentage after platform fee.
        Example:
        Platform fee = 1%
        School receives = 99%
        """

        return 100 - float(self.platform_fee_percentage)