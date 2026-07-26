from datetime import date, timedelta

from django.db import models
from django.utils import timezone


class SchoolSettings(models.Model):
    """
    Main school profile.
    Only one record should normally exist.
    """

    school_name = models.CharField(
        max_length=200,
        default="Green Apple Academy"
    )

    motto = models.CharField(
        max_length=255,
        blank=True
    )

    logo = models.ImageField(
        upload_to="school/logo/",
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    website = models.URLField(
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

    currency = models.CharField(
        max_length=10,
        default="ZMW"
    )

    academic_year = models.CharField(
        max_length=20,
        default="2026"
    )

    current_term = models.CharField(
        max_length=20,
        default="Term 1"
    )

    reception_enabled = models.BooleanField(default=True)

    pre_grade_enabled = models.BooleanField(default=True)

    school_open = models.TimeField(
        default="07:00"
    )

    school_close = models.TimeField(
        default="17:00"
    )

    primary_color = models.CharField(
        max_length=20,
        default="#198754"
    )

    secondary_color = models.CharField(
        max_length=20,
        default="#0d6efd"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "School Settings"
        verbose_name_plural = "School Settings"

    def __str__(self):
        return self.school_name


class Subscription(models.Model):

    STARTER = "Starter"
    PROFESSIONAL = "Professional"
    ENTERPRISE = "Enterprise"

    PLAN_CHOICES = [
        (STARTER, "Starter"),
        (PROFESSIONAL, "Professional"),
        (ENTERPRISE, "Enterprise"),
    ]

    ACTIVE = "Active"
    EXPIRED = "Expired"
    SUSPENDED = "Suspended"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (EXPIRED, "Expired"),
        (SUSPENDED, "Suspended"),
    ]

    school = models.OneToOneField(
        SchoolSettings,
        on_delete=models.CASCADE,
        related_name="subscription"
    )

    plan = models.CharField(
        max_length=30,
        choices=PLAN_CHOICES,
        default=STARTER
    )

    start_date = models.DateField(
        default=timezone.now
    )

    expiry_date = models.DateField(
        default=lambda: date.today() + timedelta(days=365)
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=ACTIVE
    )

    max_users = models.PositiveIntegerField(
        default=100
    )

    max_pupils = models.PositiveIntegerField(
        default=1000
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-expiry_date"]
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    @property
    def days_remaining(self):
        return (self.expiry_date - date.today()).days

    @property
    def is_expired(self):
        return date.today() > self.expiry_date

    def save(self, *args, **kwargs):
        if self.expiry_date < date.today():
            self.status = self.EXPIRED
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.school.school_name} - {self.plan}"