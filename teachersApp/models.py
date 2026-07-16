from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from accountsApp.models import User
from classesApp.models import ClassRoom, Subjects


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    subject = models.ManyToManyField(Subjects, related_name='assigned_subjects')
    assigned_class = models.ManyToManyField(ClassRoom, related_name='assigned_teachers')
    hire_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_teacher_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'teacher':
        Teacher.objects.get_or_create(user=instance)


class PupilReport(models.Model):
    TERM_CHOICES = [
        ('1', 'Term 1'),
        ('2', 'Term 2'),
        ('3', 'Term 3'),
    ]
    pupil = models.ForeignKey('studentsApp.Student', on_delete=models.CASCADE, related_name='reports')
    term = models.CharField(max_length=1, choices=TERM_CHOICES, default='1')
    academic_year = models.CharField(max_length=9)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(blank=True)
    is_submitted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('pupil', 'term', 'academic_year')

    def __str__(self):
        return f"{self.pupil.user.username} - Term {self.term} ({self.academic_year})"


class AcademicRecord(models.Model):
    EXAM_TYPES = [
        ('TEST', 'Test'),
        ('EXAM', 'Exam'),
    ]
    pupil = models.ForeignKey('studentsApp.Student', on_delete=models.CASCADE, related_name='academic_records')
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    term = models.CharField(max_length=1, choices=PupilReport.TERM_CHOICES, default='1')
    academic_year = models.CharField(max_length=9)
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPES)
    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    remark = models.TextField(blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    date_recorded = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_recorded']

    def __str__(self):
        return f"{self.pupil.user.username} - {self.subject.subject} - {self.get_exam_type_display()}"


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    due_date = models.DateField()
    file_upload = models.FileField(upload_to='assignments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class BehaviorLog(models.Model):
    BEHAVIOR_TYPES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
    ]
    pupil = models.ForeignKey('studentsApp.Student', on_delete=models.CASCADE, related_name='behavior_logs')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    category = models.CharField(max_length=10, choices=BEHAVIOR_TYPES, default='positive')
    note = models.TextField()
    conduct_remark = models.TextField(blank=True)
    is_report_card_remark = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.pupil.user.username} - {self.get_category_display()} on {self.date}"


class Timetable(models.Model):
    DAYS = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='timetable_entries')
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.teacher.user.username} - {self.subject.subject} - {self.get_day_display()} {self.start_time}-{self.end_time}"