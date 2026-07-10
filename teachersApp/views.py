import logging
from django.db.models import Q
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from accountsApp.mixins import AdminRequiredMixin
from .forms import TeacherAdminForm
from classesApp.models import ClassRoom, Subjects
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from studentsApp.models import Student
from attendanceApp.models import Attendance
from examsApp.models import Exam
from .models import Teacher
from accountsApp.models import Notice

logger = logging.getLogger(__name__)

# ... (keep AdminTeacherList, AdminTeacherDetail, AdminTeacherUpdate as before)

@login_required
def dashboard_teacher(request):
    teacher, created = Teacher.objects.get_or_create(user=request.user)
    if created:
        messages.info(request, "Teacher profile created automatically.")
    classes = teacher.assigned_class.all()
    subjects = teacher.subject.all()
    exams = Exam.objects.filter(class_room__in=classes).order_by('exam_date')
    notices = Notice.objects.order_by('-created_at')[:5]
    total_students = Student.objects.filter(class_room__in=classes).distinct().count()
    context = {
        "teacher": teacher,
        "classes": classes,
        "subjects": subjects,
        "exams": exams[:6],
        "exams_full": exams,
        "notices": notices,
        "stats": {
            "classes": classes.count(),
            "subjects": subjects.count(),
            "students": total_students,
            "upcoming_exams": exams.count(),
        }
    }
    return render(request, "teachersApp/dashboard.html", context)


@login_required
def teacher_class_detail(request, class_id):
    try:
        teacher, created = Teacher.objects.get_or_create(user=request.user)
        if created:
            messages.info(request, "Teacher profile created automatically.")

        classroom = get_object_or_404(ClassRoom, id=class_id)

        if classroom not in teacher.assigned_class.all():
            messages.error(request, "You are not assigned to this class.")
            return redirect("dashboard_teacher")

        # Pre-fetch with select_related to avoid missing relations
        students = Student.objects.filter(class_room=classroom).select_related('parent', 'parent__user', 'user')
        today = now().date()

        if request.method == "POST":
            for student in students:
                status = request.POST.get(f"status_{student.id}")
                if status:
                    Attendance.objects.update_or_create(
                        student=student,
                        date=today,
                        defaults={"status": status, "teacher": teacher}
                    )
            messages.success(request, "Attendance saved.")
            return redirect("teacher_class_detail", class_id=classroom.id)

        # Get today's attendance
        attendance_records = Attendance.objects.filter(student__in=students, date=today)
        attendance_map = {record.student.id: record.status for record in attendance_records}

        # Build safe student data – parent_user is either a User object or None
        student_data = []
        for student in students:
            parent_user = None
            if hasattr(student, 'parent') and student.parent and hasattr(student.parent, 'user'):
                parent_user = student.parent.user  # could be None
            student_data.append({
                'student': student,
                'today_status': attendance_map.get(student.id, ''),
                'parent_user': parent_user,
            })

        return render(request, "teachersApp/class_detail.html", {
            "classroom": classroom,
            "student_data": student_data,
            "today": today,
        })
    except Exception as e:
        logger.error(f"Error in teacher_class_detail for class {class_id}: {str(e)}", exc_info=True)
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("dashboard_teacher")