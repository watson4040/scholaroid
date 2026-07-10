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

# ---- Admin views (unchanged) ----
class AdminTeacherList(AdminRequiredMixin, ListView):
    model = Teacher
    template_name = 'teachersApp/admin_teacher_list.html'
    paginate_by = 12

    def get_queryset(self):
        qs = Teacher.objects.select_related('user').prefetch_related('subject', 'assigned_class')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__username__icontains=q) |
                Q(subject__name__icontains=q) |
                Q(assigned_class__name__icontains=q) |
                Q(assigned_class__section__icontains=q)
            ).distinct()
        return qs.order_by('user__first_name')

class AdminTeacherDetail(AdminRequiredMixin, DetailView):
    model = Teacher
    template_name = 'teachersApp/admin_teacher_detail.html'

    def get_queryset(self):
        return Teacher.objects.select_related('user').prefetch_related('subject', 'assigned_class')


class AdminTeacherUpdate(AdminRequiredMixin, UpdateView):
    model = Teacher
    form_class = TeacherAdminForm
    template_name = 'teachersApp/admin_teacher_edit.html'

    def get_success_url(self):
        messages.success(self.request, "Teacher updated.")
        return reverse_lazy('admin_teacher_detail', kwargs={'pk': self.object.pk})


# ---- Teacher Dashboard ----
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


# ---- Attendance Page ----
@login_required
def teacher_class_detail(request, class_id):
    # Ensure teacher exists
    teacher, created = Teacher.objects.get_or_create(user=request.user)
    if created:
        messages.info(request, "Teacher profile created automatically.")

    classroom = get_object_or_404(ClassRoom, id=class_id)

    # Authorize
    if classroom not in teacher.assigned_class.all():
        messages.error(request, "You are not assigned to this class.")
        return redirect("dashboard_teacher")

    students = Student.objects.filter(class_room=classroom).select_related('parent', 'parent__user', 'user')
    today = now().date()

    # POST: save attendance
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

    # GET: load existing attendance
    attendance_records = Attendance.objects.filter(student__in=students, date=today)
    attendance_map = {record.student.id: record.status for record in attendance_records}

    # Build safe student data
    student_data = []
    for student in students:
        parent_user = None
        if student.parent and student.parent.user:
            parent_user = student.parent.user
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