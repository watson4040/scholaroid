from django.db import models

from accountsApp.models import User
from classesApp.models import ClassRoom, Subjects


# ============================================================
# TEACHER
# ============================================================

class Teacher(models.Model):
    """
    Teacher profile linked to a system User.

    The actual User role must be:
        teacher

    Teacher profiles can be assigned:
        - multiple subjects
        - multiple classes
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
        limit_choices_to={
            "role": "teacher",
        },
    )

    subject = models.ManyToManyField(
        Subjects,
        related_name="assigned_teachers",
        blank=True,
    )

    assigned_class = models.ManyToManyField(
        ClassRoom,
        related_name="class_teachers",
        blank=True,
    )

    hire_date = models.DateField(
        auto_now_add=True,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = [
            "user__username",
        ]

        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"

    def __str__(self):
        full_name = self.user.get_full_name().strip()

        return (
            full_name
            if full_name
            else self.user.username
        )


# ============================================================
# PUPIL REPORT
# ============================================================

class PupilReport(models.Model):

    TERM_CHOICES = [
        ("1", "Term 1"),
        ("2", "Term 2"),
        ("3", "Term 3"),
    ]

    pupil = models.ForeignKey(
        "studentsApp.Student",
        on_delete=models.CASCADE,
        related_name="reports",
    )

    term = models.CharField(
        max_length=1,
        choices=TERM_CHOICES,
        default="1",
    )

    academic_year = models.CharField(
        max_length=9,
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pupil_reports",
    )

    comment = models.TextField(
        blank=True,
    )

    is_submitted = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "pupil",
                    "term",
                    "academic_year",
                ],
                name="unique_pupil_term_academic_year_report",
            ),
        ]

        ordering = [
            "-academic_year",
            "term",
        ]

    def __str__(self):
        return (
            f"{self.pupil.user.username} - "
            f"Term {self.term} "
            f"({self.academic_year})"
        )


# ============================================================
# ACADEMIC RECORD
# ============================================================

class AcademicRecord(models.Model):

    EXAM_TYPES = [
        ("TEST", "Test"),
        ("EXAM", "Exam"),
    ]

    pupil = models.ForeignKey(
        "studentsApp.Student",
        on_delete=models.CASCADE,
        related_name="academic_records",
    )

    subject = models.ForeignKey(
        Subjects,
        on_delete=models.CASCADE,
    )

    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
    )

    term = models.CharField(
        max_length=1,
        choices=PupilReport.TERM_CHOICES,
        default="1",
    )

    academic_year = models.CharField(
        max_length=9,
    )

    exam_type = models.CharField(
        max_length=10,
        choices=EXAM_TYPES,
    )

    marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    max_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100,
    )

    remark = models.TextField(
        blank=True,
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="academic_records",
    )

    date_recorded = models.DateField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-date_recorded",
        ]

    def __str__(self):
        return (
            f"{self.pupil.user.username} - "
            f"{self.subject.subject} - "
            f"{self.get_exam_type_display()}"
        )


# ============================================================
# ASSIGNMENT
# ============================================================

class Assignment(models.Model):

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField()

    subject = models.ForeignKey(
        Subjects,
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    due_date = models.DateField()

    file_upload = models.FileField(
        upload_to="assignments/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return self.title


# ============================================================
# BEHAVIOR LOG
# ============================================================

class BehaviorLog(models.Model):

    BEHAVIOR_TYPES = [
        ("positive", "Positive"),
        ("negative", "Negative"),
    ]

    pupil = models.ForeignKey(
        "studentsApp.Student",
        on_delete=models.CASCADE,
        related_name="behavior_logs",
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="behavior_logs",
    )

    category = models.CharField(
        max_length=10,
        choices=BEHAVIOR_TYPES,
        default="positive",
    )

    note = models.TextField()

    conduct_remark = models.TextField(
        blank=True,
    )

    is_report_card_remark = models.BooleanField(
        default=False,
    )

    date = models.DateField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-date",
        ]

    def __str__(self):
        return (
            f"{self.pupil.user.username} - "
            f"{self.get_category_display()} - "
            f"{self.date}"
        )


# ============================================================
# TIMETABLE
# ============================================================

class Timetable(models.Model):

    DAYS = [
        ("Mon", "Monday"),
        ("Tue", "Tuesday"),
        ("Wed", "Wednesday"),
        ("Thu", "Thursday"),
        ("Fri", "Friday"),
        ("Sat", "Saturday"),
        ("Sun", "Sunday"),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="timetable_entries",
    )

    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name="timetable_entries",
    )

    subject = models.ForeignKey(
        Subjects,
        on_delete=models.CASCADE,
        related_name="timetable_entries",
    )

    day = models.CharField(
        max_length=3,
        choices=DAYS,
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "day",
            "start_time",
        ]

    def __str__(self):
        return (
            f"{self.teacher.user.username} - "
            f"{self.subject.subject} - "
            f"{self.get_day_display()} "
            f"{self.start_time}-{self.end_time}"
        )