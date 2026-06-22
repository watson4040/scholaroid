from django.db import models
from accountsApp.models import User
from classesApp.models import ClassRoom
from parentsApp.models import Parent


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    class_room = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    admission_date = models.DateField(auto_now_add=True)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, null=True, blank=True, related_name='parent_contact')
    parent_email = models.EmailField(null=True, blank=True, help_text="Parent's email for auto-linking if parent registers later")

    class Meta:
        verbose_name = "Pupil"
        verbose_name_plural = "Pupils"

    def __str__(self):
        return self.user.username


class EnrollmentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    parent_name = models.CharField(max_length=100)
    parent_email = models.EmailField()
    parent_phone = models.CharField(max_length=15, blank=True)
    pupil_name = models.CharField(max_length=100)
    pupil_dob = models.DateField()
    pupil_class = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(blank=True, help_text="Any additional info from parent")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey('accountsApp.User', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Enrollment Request"
        verbose_name_plural = "Enrollment Requests"

    def __str__(self):
        return f"{self.pupil_name} - {self.status}"