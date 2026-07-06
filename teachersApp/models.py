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