import logging
from django.db.models import Q
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from accountsApp.mixins import AdminRequiredMixin
from .forms import TeacherAdminForm, PupilReportForm
from classesApp.models import ClassRoom, Subjects
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from studentsApp.models import Student
from attendanceApp.models import Attendance
from examsApp.models import Exam
from .models import Teacher, PupilReport
from accountsApp.models import Notice

logger = logging.getLogger(__name__)

# ---- Admin views ----
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
    try:
        logger.info(f"Starting teacher_class_detail for class_id: {class_id}, user: {request.user.id}")
        teacher, created = Teacher.objects.get_or_create(user=request.user)
        if created:
            messages.info(request, "Teacher profile created automatically.")
        logger.info(f"Teacher: {teacher.id}, created: {created}")
        classroom = get_object_or_404(ClassRoom, id=class_id)
        logger.info(f"Classroom found: {classroom.id} - {classroom.name}")

        if classroom not in teacher.assigned_class.all():
            logger.warning(f"Teacher {teacher.id} not assigned to class {class_id}")
            messages.error(request, "You are not assigned to this class.")
            return redirect("dashboard_teacher")

        students = Student.objects.filter(class_room=classroom).select_related('parent', 'parent__user', 'user')
        logger.info(f"Found {students.count()} students in class {class_id}")
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

        attendance_records = Attendance.objects.filter(student__in=students, date=today)
        attendance_map = {record.student.id: record.status for record in attendance_records}

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
    except Exception as e:
        logger.error(f"ERROR in teacher_class_detail for class {class_id}: {str(e)}", exc_info=True)
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("dashboard_teacher")

# ---- Report View ----
@login_required
def pupil_report_create_or_edit(request, pupil_id, term=None, year=None):
    try:
        logger.info(f"Report view called for pupil {pupil_id}, user {request.user.id}")
        teacher = get_object_or_404(Teacher, user=request.user)
        pupil = get_object_or_404(Student, id=pupil_id)

        if pupil.class_room not in teacher.assigned_class.all():
            logger.warning(f"Pupil {pupil_id} not in teacher's classes")
            messages.error(request, "You are not allowed to report on this pupil.")
            return redirect('dashboard_teacher')

        if term is None:
            term = '1'
        if year is None:
            import datetime
            current_year = datetime.date.today().year
            year = f"{current_year}/{current_year+1}"

        logger.info(f"Attempting to get/create report for pupil {pupil_id}, term {term}, year {year}")
        report, created = PupilReport.objects.get_or_create(
            pupil=pupil,
            term=term,
            academic_year=year,
            defaults={'teacher': teacher}
        )
        logger.info(f"Report {'created' if created else 'retrieved'} with id {report.id}")

        if request.method == 'POST':
            form = PupilReportForm(request.POST, instance=report)
            if form.is_valid():
                report = form.save(commit=False)
                report.teacher = teacher
                report.save()
                logger.info(f"Report {report.id} saved successfully")
                messages.success(request, f"Report for {pupil.user.get_full_name()} saved.")
                if report.is_submitted:
                    messages.info(request, "Report has been submitted to the parent.")
                return redirect('teacher_class_detail', class_id=pupil.class_room.id)
            else:
                logger.warning(f"Form invalid: {form.errors}")
                messages.error(request, "Please correct the errors below.")
        else:
            form = PupilReportForm(instance=report)

        return render(request, 'teachersApp/report_form.html', {
            'form': form,
            'pupil': pupil,
            'report': report,
            'classroom': pupil.class_room,
        })
    except Exception as e:
        logger.error(f"CRITICAL ERROR in pupil_report_create_or_edit: {str(e)}", exc_info=True)
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('dashboard_teacher')