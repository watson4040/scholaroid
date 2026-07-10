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
    academic_year = models.CharField(max_length=9)  # e.g., "2025/2026"
    teacher = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True)
    comment = models.TextField(blank=True, help_text="Teacher's comment on pupil progress")
    is_submitted = models.BooleanField(default=False)  # when True, parent can see it
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('pupil', 'term', 'academic_year')  # one report per pupil per term

    def __str__(self):
        return f"{self.pupil.user.username} - Term {self.term} ({self.academic_year})"    