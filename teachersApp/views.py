import logging
from django.db.models import Q, Avg, Sum, Count
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from accountsApp.mixins import AdminRequiredMixin
from .forms import (
    TeacherAdminForm, PupilReportForm,
    AcademicRecordForm, AssignmentForm, BehaviorLogForm
)
from classesApp.models import ClassRoom, Subjects
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from studentsApp.models import Student
from attendanceApp.models import Attendance
from examsApp.models import Exam
from .models import Teacher, PupilReport, AcademicRecord, Assignment, BehaviorLog, Timetable
from accountsApp.models import Notice
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML  # Optional – for PDF generation, but we'll skip for simplicity
import datetime

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

# ---- Pupil Report (existing) ----
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
            current_year = datetime.date.today().year
            year = f"{current_year}/{current_year+1}"

        report, created = PupilReport.objects.get_or_create(
            pupil=pupil,
            term=term,
            academic_year=year,
            defaults={'teacher': teacher}
        )

        if request.method == 'POST':
            form = PupilReportForm(request.POST, instance=report)
            if form.is_valid():
                report = form.save(commit=False)
                report.teacher = teacher
                report.save()
                messages.success(request, f"Report for {pupil.user.get_full_name()} saved.")
                if report.is_submitted:
                    messages.info(request, "Report has been submitted to the parent.")
                return redirect('teacher_class_detail', class_id=pupil.class_room.id)
            else:
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


# ==========================================================
#  NEW TEACHER FEATURES
# ==========================================================

# ---------- Timetable ----------
@login_required
def teacher_timetable(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    timetable_entries = Timetable.objects.filter(teacher=teacher).select_related('class_room', 'subject')
    # Group by day
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    timetable = {day: [] for day in days}
    for entry in timetable_entries:
        timetable[entry.day].append(entry)
    context = {
        'teacher': teacher,
        'timetable': timetable,
        'days': days,
    }
    return render(request, 'teachersApp/timetable.html', context)


# ---------- Assignments ----------
@login_required
def teacher_assignments(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    assignments = Assignment.objects.filter(teacher=teacher).order_by('-created_at')
    return render(request, 'teachersApp/assignments.html', {'assignments': assignments, 'teacher': teacher})

@login_required
def teacher_assignment_create(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        form.instance.teacher = teacher
        if form.is_valid():
            assignment = form.save()
            messages.success(request, "Assignment posted successfully.")
            return redirect('teacher_assignments')
    else:
        form = AssignmentForm()
        # Limit choices to teacher's classes and subjects
        form.fields['class_room'].queryset = teacher.assigned_class.all()
        form.fields['subject'].queryset = teacher.subject.all()
    return render(request, 'teachersApp/assignment_form.html', {'form': form, 'teacher': teacher})


# ---------- Academic (Enter Marks) ----------
@login_required
def teacher_academic(request, class_id=None, subject_id=None):
    teacher = get_object_or_404(Teacher, user=request.user)
    if class_id and subject_id:
        classroom = get_object_or_404(ClassRoom, id=class_id)
        subject = get_object_or_404(Subjects, id=subject_id)
        if classroom not in teacher.assigned_class.all() or subject not in teacher.subject.all():
            messages.error(request, "You are not assigned to this class or subject.")
            return redirect('dashboard_teacher')
        students = Student.objects.filter(class_room=classroom)
        if request.method == 'POST':
            for student in students:
                marks = request.POST.get(f'marks_{student.id}')
                max_marks = request.POST.get(f'max_marks_{student.id}')
                exam_type = request.POST.get('exam_type')
                term = request.POST.get('term')
                academic_year = request.POST.get('academic_year')
                if marks and max_marks and exam_type and term and academic_year:
                    AcademicRecord.objects.update_or_create(
                        pupil=student,
                        subject=subject,
                        class_room=classroom,
                        term=term,
                        academic_year=academic_year,
                        exam_type=exam_type,
                        defaults={
                            'marks': float(marks),
                            'max_marks': float(max_marks),
                            'teacher': teacher,
                        }
                    )
            messages.success(request, "Marks saved successfully.")
            return redirect('teacher_academic', class_id=classroom.id, subject_id=subject.id)
        context = {
            'classroom': classroom,
            'subject': subject,
            'students': students,
            'teacher': teacher,
        }
        return render(request, 'teachersApp/academic.html', context)
    else:
        # Show selection form
        classes = teacher.assigned_class.all()
        subjects = teacher.subject.all()
        return render(request, 'teachersApp/academic_select.html', {
            'classes': classes,
            'subjects': subjects,
            'teacher': teacher,
        })


# ---------- Behavior Log ----------
@login_required
def teacher_behavior(request, pupil_id=None):
    teacher = get_object_or_404(Teacher, user=request.user)
    if pupil_id:
        pupil = get_object_or_404(Student, id=pupil_id)
        if pupil.class_room not in teacher.assigned_class.all():
            messages.error(request, "You are not assigned to this pupil's class.")
            return redirect('dashboard_teacher')
        if request.method == 'POST':
            form = BehaviorLogForm(request.POST)
            if form.is_valid():
                log = form.save(commit=False)
                log.teacher = teacher
                log.pupil = pupil
                log.save()
                messages.success(request, "Behavior log added.")
                return redirect('teacher_class_detail', class_id=pupil.class_room.id)
        else:
            form = BehaviorLogForm(initial={'pupil': pupil})
            form.fields['pupil'].widget = forms.HiddenInput()
        return render(request, 'teachersApp/behavior_form.html', {'form': form, 'pupil': pupil, 'teacher': teacher})
    else:
        # List behavior logs for teacher's classes
        logs = BehaviorLog.objects.filter(teacher=teacher).select_related('pupil').order_by('-date')
        return render(request, 'teachersApp/behavior_list.html', {'logs': logs, 'teacher': teacher})


# ---------- Class Performance ----------
@login_required
def teacher_class_performance(request, class_id):
    teacher = get_object_or_404(Teacher, user=request.user)
    classroom = get_object_or_404(ClassRoom, id=class_id)
    if classroom not in teacher.assigned_class.all():
        messages.error(request, "You are not assigned to this class.")
        return redirect('dashboard_teacher')
    students = Student.objects.filter(class_room=classroom)
    subjects = teacher.subject.all()
    performance_data = []
    for student in students:
        row = {'student': student}
        total_marks = 0
        count = 0
        for subject in subjects:
            records = AcademicRecord.objects.filter(pupil=student, subject=subject, class_room=classroom)
            avg = records.aggregate(Avg('marks'))['marks__avg']
            row[subject.id] = round(avg, 2) if avg else '-'
            if avg:
                total_marks += avg
                count += 1
        row['average'] = round(total_marks / count, 2) if count else '-'
        performance_data.append(row)
    context = {
        'classroom': classroom,
        'students': performance_data,
        'subjects': subjects,
        'teacher': teacher,
    }
    return render(request, 'teachersApp/class_performance.html', context)


# ---------- Print Class List ----------
@login_required
def teacher_print_class_list(request, class_id):
    teacher = get_object_or_404(Teacher, user=request.user)
    classroom = get_object_or_404(ClassRoom, id=class_id)
    if classroom not in teacher.assigned_class.all():
        messages.error(request, "You are not assigned to this class.")
        return redirect('dashboard_teacher')
    students = Student.objects.filter(class_room=classroom).select_related('user')
    context = {
        'classroom': classroom,
        'students': students,
        'teacher': teacher,
        'today': now().date(),
    }
    return render(request, 'teachersApp/print_class_list.html', context)


# ---------- Print Subject Results ----------
@login_required
def teacher_print_results(request, class_id, subject_id):
    teacher = get_object_or_404(Teacher, user=request.user)
    classroom = get_object_or_404(ClassRoom, id=class_id)
    subject = get_object_or_404(Subjects, id=subject_id)
    if classroom not in teacher.assigned_class.all() or subject not in teacher.subject.all():
        messages.error(request, "You are not assigned to this class or subject.")
        return redirect('dashboard_teacher')
    students = Student.objects.filter(class_room=classroom).select_related('user')
    results = []
    for student in students:
        records = AcademicRecord.objects.filter(pupil=student, subject=subject, class_room=classroom)
        ca = records.filter(exam_type='CA').first()
        test = records.filter(exam_type='TEST').first()
        exam = records.filter(exam_type='EXAM').first()
        total = 0
        if ca:
            total += ca.marks
        if test:
            total += test.marks
        if exam:
            total += exam.marks
        results.append({
            'student': student,
            'ca': ca.marks if ca else '-',
            'test': test.marks if test else '-',
            'exam': exam.marks if exam else '-',
            'total': total if (ca or test or exam) else '-',
        })
    context = {
        'classroom': classroom,
        'subject': subject,
        'results': results,
        'teacher': teacher,
        'today': now().date(),
    }
    return render(request, 'teachersApp/print_results.html', context)