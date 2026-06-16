from django.contrib import admin
from .models import Student, EnrollmentRequest
from django.core.mail import send_mail
from django.conf import settings

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'class_room', 'admission_date', 'parent')
    search_fields = ('user__username', 'user__email')

@admin.register(EnrollmentRequest)
class EnrollmentRequestAdmin(admin.ModelAdmin):
    list_display = ('pupil_name', 'parent_name', 'parent_email', 'status', 'created_at')
    list_filter = ('status', 'pupil_class')
    actions = ['approve_enrollments']

def approve_enrollments(self, request, queryset):
    from django.utils import timezone
    from accountsApp.models import User
    from parentsApp.models import Parent
    for req in queryset.filter(status='pending'):
        # Create parent user
        parent_user, created = User.objects.get_or_create(
            username=req.parent_email,
            defaults={
                'email': req.parent_email,
                'first_name': req.parent_name.split()[0] if ' ' in req.parent_name else req.parent_name,
                'last_name': req.parent_name.split()[-1] if ' ' in req.parent_name else '',
                'role': 'parent',
            }
        )
        if created:
            parent_user.set_password(User.objects.make_random_password())
            parent_user.save()
            Parent.objects.get_or_create(user=parent_user, defaults={'phone_number': req.parent_phone})

        # Create pupil user
        base_username = req.pupil_name.replace(' ', '').lower()
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        pupil_user = User.objects.create_user(
            username=username,
            email=f"{username}@temp.local",
            first_name=req.pupil_name.split()[0] if ' ' in req.pupil_name else req.pupil_name,
            last_name=req.pupil_name.split()[-1] if ' ' in req.pupil_name else '',
            password=User.objects.make_random_password(),
            role='student'
        )
        Student.objects.create(
            user=pupil_user,
            class_room=req.pupil_class,
            parent=parent_user.parent if hasattr(parent_user, 'parent') else None
        )
        req.status = 'approved'
        req.approved_at = timezone.now()
        req.approved_by = request.user
        req.save()

        # Send email notification
        send_mail(
            subject='Enrollment Approved – Scholaroid',
            message=f"""
Dear {parent_user.first_name or parent_user.email},

Your child {pupil_user.first_name} has been officially enrolled.

Parent login details:
Username: {parent_user.username}
Password: (the one you set during registration, or use 'Forgot Password')

Student login details:
Username: {pupil_user.username}
Password: (ask the admin to set a password)

Please log in at https://yourdomain.com to view your child's progress.

Thank you,
Scholaroid School
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[parent_user.email],
            fail_silently=False,
        )
    self.message_user(request, f"{queryset.count()} enrollment(s) approved.")