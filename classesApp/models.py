
from django.db import models

from schoolsApp.models import School


class ClassRoom(models.Model):
    """
    A class/stream belonging to a specific school.

    The school relationship is nullable temporarily so existing
    classes can be migrated safely. New classes should always be
    assigned to a school by the application.
    """

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="classrooms",
        null=True,
        blank=True,
        help_text="School this class belongs to.",
    )

    name = models.CharField(
        max_length=50,
    )

    section = models.CharField(
        max_length=10,
    )

    capacity = models.PositiveIntegerField(
        default=25,
    )

    class Meta:
        ordering = ["school__name", "name", "section"]
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        school_name = self.school.name if self.school else "No School"
        return f"{self.name} - {self.section} ({school_name})"


class Subjects(models.Model):
    """
    Academic subject offered by the school system.

    Subject remains independent for now because the existing
    Teacher model already uses it through a ManyToManyField.
    """

    subject = models.CharField(
        max_length=50,
    )

    class Meta:
        ordering = ["subject"]
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def __str__(self):
        return self.subject

