from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q
from accountsApp.forms import *
from accountsApp.forms import ChangePasswordForm
from accountsApp.models import Notice
from studentsApp.models import Student
from teachersApp.models import Teacher
from parentsApp.models import Parent
from classesApp.models import ClassRoom
from attendanceApp.models import Attendance
from examsApp.models import Exam, ExamResult
from messagingApp.models import Message

def home(request):
    return render(request, 'home.html')

def register_admin(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect_url': reverse('home')})
            return redirect('home')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {f: list(v) for f, v in form.errors.items()}
                return JsonResponse({'success': False, 'field_errors': errors}, status=400)
    else:
        form = AdminRegistrationForm()
    return render(request, 'accountsApp/register.html', {'form': form})

def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect_url': reverse('home')})
            return redirect('home')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {f: list(v) for f, v in form.errors.items()}
                return JsonResponse({'success': False, 'field_errors': errors}, status=400)
    else:
        form = TeacherRegistrationForm()
    return render(request, 'accountsApp/register.html', {'form': form})

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect_url': reverse('home')})
            return redirect('home')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {f: list(v) for f, v in form.errors.items()}
                return JsonResponse({'success': False, 'field_errors': errors}, status=400)
    else:
        form = StudentRegistrationForm()
    return render(request, 'accountsApp/register.html', {'form': form})

def register_parent(request):
    if request.method == 'POST':
        form = ParentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            try:
                parent_profile = Parent.objects.get(user=user)
                from studentsApp.models import Student
                matches = Student.objects.filter(parent__isnull=True, parent_email__iexact=user.email)
                for stu in matches:
                    stu.parent = parent_profile
                    stu.save(update_fields=['parent'])
                if matches.exists():
                    messages.success(request, f"Linked {matches.count()} student(s) to your parent account.")
            except Parent.DoesNotExist:
                pass
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect_url': reverse('home')})
            return redirect('home')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {f: list(v) for f, v in form.errors.items()}
                return JsonResponse({'success': False, 'field_errors': errors}, status=400)
    else:
        form = ParentRegistrationForm()
    return render(request, 'accountsApp/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect_url': reverse('home')})
            return redirect('home')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': ['Invalid credentials.']}, status=400)
            messages.error(request, "Invalid credentials. Please try again.")
    return render(request, 'accountsApp/login.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard_admin(request):
    if request.user.role != 'admin':
        return render(request, 'errors/403.html')
    context = {
        "student_count": Student.objects.count(),
        "teacher_count": Teacher.objects.count(),
        "parent_count": Parent.objects.count(),
        "class_count": ClassRoom.objects.count(),
        "exam_count": Exam.objects.count(),
        "notification_count": Notice.objects.count(),
        "recent_attendance": Attendance.objects.order_by('-date')[:5],
        "recent_messages": Message.objects.order_by('-created_at')[:5],
        "recent_exams": Exam.objects.order_by('-exam_date')[:5],
        "recent_students": Student.objects.order_by('-admission_date')[:5],
        "recent_notifications": Notice.objects.order_by('-created_at')[:5],
        "active_users": get_user_model().objects.filter(is_active=True).count(),
    }
    return render(request, "accountsApp/dashboard.html", context)

@login_required
def dashboard_student(request):
    student = get_object_or_404(Student, user=request.user)
    all_attendance = Attendance.objects.filter(student=student)
    total = all_attendance.count()
    if total > 0:
        present = all_attendance.filter(status='present').count()
        attendance_percentage = round((present / total) * 100)
    else:
        attendance_percentage = 0
    attendance_records = all_attendance.order_by('-date')[:10]
    exams = Exam.objects.filter(class_room=student.class_room).order_by('exam_date')
    notices = Notice.objects.order_by('-created_at')[:5]
    student_results = ExamResult.objects.filter(student=student).select_related('exam__subject')
    context = {
        'student': student,
        'attendance_records': attendance_records,
        'attendance_percentage': attendance_percentage,
        'exams': exams,
        'notices': notices,
        'student_results': student_results,
    }
    return render(request, 'accountsApp/dashboard_student.html', context)

@login_required
def dashboard_teacher(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    classes = teacher.class_assigned.all() if hasattr(teacher, 'class_assigned') else []
    students_count = sum(c.students.count() for c in classes)
    recent_exams = Exam.objects.filter(class_room__in=classes).order_by('exam_date')[:5]
    recent_attendance = Attendance.objects.filter(student__class_room__in=classes).order_by('-date')[:10]
    notices = Notice.objects.order_by('-created_at')[:5]
    
    # Simple, reliable context without resources
    context = {
        'teacher': teacher,
        'classes': classes,
        'students_count': students_count,
        'recent_exams': recent_exams,
        'recent_attendance': recent_attendance,
        'notices': notices,
    }
    return render(request, 'accountsApp/dashboard_teacher.html', context)

@login_required
def dashboard_parent(request):
    parent = get_object_or_404(Parent, user=request.user)
    children = Student.objects.filter(parent=parent)
    children_data = []
    for child in children:
        att = Attendance.objects.filter(student=child).order_by('-date')[:5]
        exams = Exam.objects.filter(class_room=child.class_room).order_by('exam_date')[:3]
        children_data.append({
            'student': child,
            'attendance': att,
            'exams': exams,
        })
    notices = Notice.objects.order_by('-created_at')[:5]

    # Get recent messages for this parent (where parent is sender or recipient)
    recent_messages = Message.objects.filter(
        Q(sender=parent.user) | Q(recipient=parent.user)
    ).order_by('-created_at')[:5]

    context = {
        'parent': parent,
        'children': children,
        'children_data': children_data,
        'notices': notices,
        'recent_messages': recent_messages,
    }
    return render(request, 'accountsApp/dashboard_parent.html', context)

User = get_user_model()

@login_required
def profile_view(request):
    if request.method == 'POST':
        if 'remove_photo' in request.POST:
            if request.user.profile_photo:
                request.user.profile_photo.delete(save=False)
            request.user.profile_photo = None
            request.user.save()
            messages.success(request, "Profile photo removed.")
            return redirect('profile')
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accountsApp/profile.html', {'form': form})

@login_required
def notice_list(request):
    notices = Notice.objects.order_by('-created_at')
    return render(request, "accountsApp/notice_list.html", {"notices": notices})

@login_required
def notice_create(request):
    user = request.user
    if not user.role == 'admin':
        return redirect("notice_list")
    if request.method == "POST":
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.created_by = request.user
            notice.save()
            return redirect("notice_list")
    else:
        form = NoticeForm()
    return render(request, "accountsApp/notice_form.html", {"form": form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('profile')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'accountsApp/change_password.html', {'form': form})