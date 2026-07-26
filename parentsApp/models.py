from django.db import models
from accountsApp.models import User


class Parent(models.Model):
    """
    Parent profile linked to a system user.

    The profile is automatically created from
    accountsApp.signals when the user role is 'parent'.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="parent_profile",
        limit_choices_to={"role": "parent"},
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents"
        ordering = ["user__username"]

    def __str__(self):
        full_name = self.user.get_full_name().strip()

        if full_name:
            return full_name

        return self.user.username