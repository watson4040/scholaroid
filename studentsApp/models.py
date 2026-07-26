from django.db import models
from accountsApp.models import User
from classesApp.models import ClassRoom
from parentsApp.models import Parent


class Student(models.Model):
    """
    Pupil profile.

    Internally the model is named Student for compatibility,
    but everywhere in the UI it is displayed as Pupil.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "pupil"},
        related_name="student_profile",
    )

    parent = models.ForeignKey(
        Parent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pupils",
        help_text="Parent or guardian linked to this pupil.",
    )

    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )

    admission_date = models.DateField(
        auto_now_add=True,
    )

    parent_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Parent email used for automatic linking.",
    )

    class Meta:
        verbose_name = "Pupil"
        verbose_name_plural = "Pupils"
        ordering = ["user__username"]

    def __str__(self):
        full_name = self.user.get_full_name().strip()
        return full_name if full_name else self.user.username


class EnrollmentRequest(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    parent_name = models.CharField(max_length=100)

    parent_email = models.EmailField()

    parent_phone = models.CharField(
        max_length=15,
        blank=True,
    )

    pupil_name = models.CharField(max_length=100)

    pupil_dob = models.DateField()

    pupil_class = models.ForeignKey(
        ClassRoom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollment_requests",
    )

    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_enrollment_requests",
    )

    class Meta:
        verbose_name = "Enrollment Request"
        verbose_name_plural = "Enrollment Requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.pupil_name} ({self.get_status_display()})"