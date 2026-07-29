import logging
import datetime

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import ListView, DetailView, UpdateView

from accountsApp.mixins import AdminRequiredMixin
from accountsApp.models import Notice
from attendanceApp.models import Attendance
from classesApp.models import ClassRoom, Subjects
from examsApp.models import Exam
from resourcesApp.models import Resource
from studentsApp.models import Student

from .forms import (
TeacherAdminForm,
PupilReportForm,
AssignmentForm,
BehaviorLogForm,
)

from .models import (
Teacher,
PupilReport,
AcademicRecord,
Assignment,
BehaviorLog,
Timetable,
)

logger = logging.getLogger(**name**)

# ============================================================

# ADMIN TEACHER VIEWS

# ============================================================

class AdminTeacherList(AdminRequiredMixin, ListView):
model = Teacher
template_name = "teachersApp/admin_teacher_list.html"
paginate_by = 12

```
def get_queryset(self):
    qs = (
        Teacher.objects
        .select_related("user")
        .prefetch_related("subject", "assigned_class")
    )

    q = self.request.GET.get("q")

    if q:
        qs = qs.filter(
            Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__username__icontains=q)
            | Q(subject__subject__icontains=q)
            | Q(assigned_class__name__icontains=q)
            | Q(assigned_class__section__icontains=q)
        ).distinct()

    return qs.order_by("user__first_name")
```

class AdminTeacherDetail(AdminRequiredMixin, DetailView):
model = Teacher
template_name = "teachersApp/admin_teacher_detail.html"

```
def get_queryset(self):
    return (
        Teacher.objects
        .select_related("user")
        .prefetch_related("subject", "assigned_class")
    )
```

class AdminTeacherUpdate(AdminRequiredMixin, UpdateView):
model = Teacher
form_class = TeacherAdminForm
template_name = "teachersApp/admin_teacher_edit.html"

```
def get_success_url(self):
    messages.success(self.request, "Teacher updated.")
    return reverse_lazy(
        "admin_teacher_detail",
        kwargs={"pk": self.object.pk},
    )
```

# ============================================================

# TEACHER DASHBOARD ENTRY

# ============================================================

@login_required
def dashboard_teacher(request):
"""
Main teacher dashboard entry point.

```
The actual dashboard is dashboard_final.
"""
return redirect("dashboard_final")
```

# ============================================================

# TEACHER DASHBOARD

# ============================================================

@login_required
def dashboard_final(request):
"""
Production teacher dashboard.

```
IMPORTANT:
ClassRoom does NOT have a school field.

School membership is stored on User and Student/Pupil.
Therefore we NEVER do:

    teacher.assigned_class.filter(school=school)

because that produces:

    FieldError: Cannot resolve keyword 'school'

Instead:
- teacher classes come from Teacher.assigned_class
- pupils are filtered by Student.school
- notices are filtered by creator's school
"""

try:
    teacher = get_object_or_404(
        Teacher.objects.select_related(
            "user",
            "user__school",
        ),
        user=request.user,
    )

    # ----------------------------------------------------
    # IMPORTANT:
    # ClassRoom has NO school field.
    # Do NOT filter assigned_class by school.
    # ----------------------------------------------------

    assigned_classes = (
        teacher.assigned_class
        .all()
        .order_by("name", "section")
    )

    assigned_subjects = (
        teacher.subject
        .all()
        .order_by("subject")
    )

    # ----------------------------------------------------
    # SCHOOL
    # ----------------------------------------------------

    school = getattr(request.user, "school", None)

    # ----------------------------------------------------
    # PUPILS
    # ----------------------------------------------------

    pupils = (
        Student.objects
        .filter(class_room__in=assigned_classes)
        .select_related(
            "user",
            "school",
            "class_room",
        )
    )

    # Student/Pupil DOES have a school field, so this is
    # the correct place to apply school filtering.
    if school is not None:
        pupils = pupils.filter(school=school)

    pupils = pupils.order_by(
        "user__first_name",
        "user__last_name",
    )

    # ----------------------------------------------------
    # EXAMS
    # ----------------------------------------------------

    upcoming_exams = (
        Exam.objects
        .filter(class_room__in=assigned_classes)
        .select_related(
            "subject",
            "class_room",
        )
        .order_by("exam_date")
    )

    # ----------------------------------------------------
    # NOTICES
    # ----------------------------------------------------

    notices = Notice.objects.select_related(
        "created_by"
    )

    if school is not None:
        notices = notices.filter(
            created_by__school=school
        )

    notices = notices.order_by(
        "-created_at"
    )[:8]

    # ----------------------------------------------------
    # ASSIGNMENTS
    # ----------------------------------------------------

    assignments = (
        Assignment.objects
        .filter(teacher=teacher)
        .select_related(
            "subject",
            "class_room",
        )
        .order_by("-created_at")[:5]
    )

    # ----------------------------------------------------
    # TIMETABLE
    # ----------------------------------------------------

    timetable_today = (
        Timetable.objects
        .filter(teacher=teacher)
        .select_related(
            "class_room",
            "subject",
        )
        .order_by(
            "day",
            "start_time",
        )
    )

    # ----------------------------------------------------
    # CONTEXT
    # ----------------------------------------------------

    context = {
        "teacher": teacher,
        "school": school,

        "classes": assigned_classes,
        "subjects": assigned_subjects,

        "pupils": pupils[:20],
        "students": pupils[:20],

        "exams": upcoming_exams[:6],

        "assignments": assignments,

        "today_timetable": timetable_today,
        "timetable": timetable_today,

        "notices": notices,

        "stats": {
            "classes": assigned_classes.count(),
            "subjects": assigned_subjects.count(),
            "students": pupils.count(),
            "pupils": pupils.count(),
            "upcoming_exams": upcoming_exams.count(),
        },
    }

    return render(
        request,
        "teachersApp/dashboard_final.html",
        context,
    )

except Exception:
    logger.exception(
        "Teacher dashboard failed for user %s",
        request.user.pk,
    )

    messages.error(
        request,
        "Unable to load your teacher dashboard. Please try again.",
    )

    return redirect("home")
```

# ============================================================

# TEACHER CLASS DETAIL / ATTENDANCE

# ============================================================

@login_required
def teacher_class_detail(request, class_id):
try:
logger.info(
"Starting teacher_class_detail for class_id=%s, user=%s",
class_id,
request.user.id,
)

```
    teacher = get_object_or_404(
        Teacher,
        user=request.user,
    )

    classroom = get_object_or_404(
        ClassRoom,
        id=class_id,
    )

    if not teacher.assigned_class.filter(
        id=classroom.id
    ).exists():
        logger.warning(
            "Teacher %s is not assigned to class %s",
            teacher.id,
            class_id,
        )

        messages.error(
            request,
            "You are not assigned to this class.",
        )

        return redirect("dashboard_final")

    students = (
        Student.objects
        .filter(class_room=classroom)
        .select_related(
            "parent",
            "parent__user",
            "user",
        )
    )

    # Keep teacher's school and pupil school consistent.
    school = getattr(request.user, "school", None)

    if school is not None:
        students = students.filter(
            school=school
        )

    today = now().date()

    if request.method == "POST":

        for student in students:

            status = request.POST.get(
                f"status_{student.id}"
            )

            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    date=today,
                    defaults={
                        "status": status,
                        "teacher": teacher,
                    },
                )

        messages.success(
            request,
            "Attendance saved.",
        )

        return redirect(
            "teacher_class_detail",
            class_id=classroom.id,
        )

    attendance_records = Attendance.objects.filter(
        student__in=students,
        date=today,
    )

    attendance_map = {
        record.student.id: record.status
        for record in attendance_records
    }

    student_data = []

    for student in students:

        parent_user = None

        if student.parent and student.parent.user:
            parent_user = student.parent.user

        student_data.append(
            {
                "student": student,
                "pupil": student,
                "today_status": attendance_map.get(
                    student.id,
                    "",
                ),
                "parent_user": parent_user,
            }
        )

    return render(
        request,
        "teachersApp/class_detail.html",
        {
            "classroom": classroom,
            "student_data": student_data,
            "today": today,
        },
    )

except Exception as exc:

    logger.exception(
        "ERROR in teacher_class_detail for class %s",
        class_id,
    )

    messages.error(
        request,
        f"An error occurred: {str(exc)}",
    )

    return redirect("dashboard_final")
```

# ============================================================

# PUPIL REPORT

# ============================================================

@login_required
def pupil_report_create_or_edit(
request,
pupil_id,
term=None,
year=None,
):
try:

```
    logger.info(
        "Report view called for pupil %s, user %s",
        pupil_id,
        request.user.id,
    )

    teacher = get_object_or_404(
        Teacher,
        user=request.user,
    )

    pupil = get_object_or_404(
        Student,
        id=pupil_id,
    )

    if not teacher.assigned_class.filter(
        id=pupil.class_room_id
    ).exists():
        logger.warning(
            "Pupil %s is not in teacher %s classes",
            pupil_id,
            teacher.id,
        )

        messages.error(
            request,
            "You are not allowed to report on this pupil.",
        )

        return redirect("dashboard_final")

    if term is None:
        term = "1"

    if year is None:
        current_year = datetime.date.today().year
        year = f"{current_year}/{current_year + 1}"

    report, created = PupilReport.objects.get_or_create(
        pupil=pupil,
        term=term,
        academic_year=year,
        defaults={
            "teacher": teacher,
        },
    )

    if request.method == "POST":

        form = PupilReportForm(
            request.POST,
            instance=report,
        )

        if form.is_valid():

            report = form.save(
                commit=False
            )

            report.teacher = teacher

            report.save()

            messages.success(
                request,
                f"Report for {pupil.user.get_full_name()} saved.",
            )

            if report.is_submitted:
                messages.info(
                    request,
                    "Report has been submitted to the parent.",
                )

            return redirect(
                "teacher_class_detail",
                class_id=pupil.class_room.id,
            )

        messages.error(
            request,
            "Please correct the errors below.",
        )

    else:
        form = PupilReportForm(
            instance=report
        )

    return render(
        request,
        "teachersApp/report_form.html",
        {
            "form": form,
            "pupil": pupil,
            "report": report,
            "classroom": pupil.class_room,
        },
    )

except Exception as exc:

    logger.exception(
        "CRITICAL ERROR in pupil_report_create_or_edit"
    )

    messages.error(
        request,
        f"An error occurred: {str(exc)}",
    )

    return redirect("dashboard_final")
```

# ============================================================

# TIMETABLE

# ============================================================

@login_required
def teacher_timetable(request):

```
try:

    teacher = get_object_or_404(
        Teacher,
        user=request.user,
    )

    timetable_entries = (
        Timetable.objects
        .filter(teacher=teacher)
        .select_related(
            "class_room",
            "subject",
        )
    )

    days = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
    ]

    timetable = {
        day: []
        for day in days
    }

    for entry in timetable_entries:

        if entry.day in timetable:
            timetable[entry.day].append(entry)

    context = {
        "teacher": teacher,
        "timetable": timetable,
        "days": days,
    }

    return render(
        request,
        "teachersApp/timetable.html",
        context,
    )

except Exception as exc:

    logger.exception(
        "Error in teacher_timetable"
    )

    return HttpResponse(
        f"Error: {exc}",
        status=500,
    )
```

# ============================================================

# ASSIGNMENTS

# ============================================================

@login_required
def teacher_assignments(request):

```
teacher = get_object_or_404(
    Teacher,
    user=request.user,
)

assignments = (
    Assignment.objects
    .filter(teacher=teacher)
    .select_related(
        "subject",
        "class_room",
    )
    .order_by("-created_at")
)

return render(
    request,
    "teachersApp/assignments.html",
    {
        "assignments": assignments,
        "teacher": teacher,
    },
)
```

@login_required
def teacher_assignment_create(request):

```
teacher = get_object_or_404(
    Teacher,
    user=request.user,
)

if request.method == "POST":

    form = AssignmentForm(
        request.POST,
        request.FILES,
    )

    form.instance.teacher = teacher

    # Restrict submitted choices to this teacher.
    form.fields["class_room"].queryset = (
        teacher.assigned_class.all()
    )

    form.fields["subject"].queryset = (
        teacher.subject.all()
    )

    if form.is_valid():

        assignment = form.save()

        messages.success(
            request,
            "Assignment posted successfully.",
        )

        return redirect(
            "teacher_assignments"
        )

else:

    form = AssignmentForm()

    form.fields["class_room"].queryset = (
        teacher.assigned_class.all()
    )

    form.fields["subject"].queryset = (
        teacher.subject.all()
    )

return render(
    request,
    "teachersApp/assignment_form.html",
    {
        "form": form,
        "teacher": teacher,
    },
)
```

# ============================================================

# ACADEMIC RECORDS

# ============================================================

@login_required
def teacher_academic(
request,
class_id=None,
subject_id=None,
):
try:

```
    teacher = get_object_or_404(
        Teacher,
        user=request.user,
    )

    if not class_id or class_id == 0:
        class_id = request.GET.get(
            "class_id"
        )

    if not subject_id or subject_id == 0:
        subject_id = request.GET.get(
            "subject_id"
        )

    if class_id:
        class_id = int(class_id)

    if subject_id:
        subject_id = int(subject_id)

    if not class_id or not subject_id:

        classes = (
            teacher.assigned_class.all()
        )

        subjects = (
            teacher.subject.all()
        )

        return render(
            request,
            "teachersApp/academic_select.html",
            {
                "classes": classes,
                "subjects": subjects,
                "teacher": teacher,
            },
        )

    classroom = get_object_or_404(
        ClassRoom,
        id=class_id,
    )

    subject = get_object_or_404(
        Subjects,
        id=subject_id,
    )

    if not teacher.assigned_class.filter(
        id=classroom.id
    ).exists() or not teacher.subject.filter(
        id=subject.id
    ).exists():

        messages.error(
            request,
            "You are not assigned to this class or subject.",
        )

        return redirect(
            "dashboard_final"
        )

    students = (
        Student.objects
        .filter(class_room=classroom)
        .select_related("user")
    )

    school = getattr(
        request.user,
        "school",
        None,
    )

    if school is not None:
        students = students.filter(
            school=school
        )

    if request.method == "POST":

        term = request.POST.get(
            "term"
        )

        academic_year = request.POST.get(
            "academic_year"
        )

        if not term or not academic_year:

            messages.error(
                request,
                "Please select a term and enter an academic year.",
            )

            return redirect(
                "teacher_academic_entry",
                class_id=classroom.id,
                subject_id=subject.id,
            )

        for student in students:

            test_marks = request.POST.get(
                f"test_{student.id}"
            )

            exam_marks = request.POST.get(
                f"exam_{student.id}"
            )

            max_marks = request.POST.get(
                f"max_marks_{student.id}"
            )

            # ----------------------------
            # TEST
            # ----------------------------

            if test_marks and test_marks.strip():

                try:

                    AcademicRecord.objects.create(
                        pupil=student,
                        subject=subject,
                        class_room=classroom,
                        term=term,
                        academic_year=academic_year,
                        exam_type="TEST",
                        marks=float(test_marks),
                        max_marks=(
                            float(max_marks)
                            if max_marks
                            else 30
                        ),
                        teacher=teacher,
                    )

                except Exception:

                    logger.exception(
                        "Error saving TEST mark for pupil %s",
                        student.id,
                    )

            # ----------------------------
            # EXAM
            # ----------------------------

            if exam_marks and exam_marks.strip():

                try:

                    AcademicRecord.objects.create(
                        pupil=student,
                        subject=subject,
                        class_room=classroom,
                        term=term,
                        academic_year=academic_year,
                        exam_type="EXAM",
                        marks=float(exam_marks),
                        max_marks=(
                            float(max_marks)
                            if max_marks
                            else 50
                        ),
                        teacher=teacher,
                    )

                except Exception:

                    logger.exception(
                        "Error saving EXAM mark for pupil %s",
                        student.id,
                    )

        messages.success(
            request,
            "Marks saved successfully.",
        )

        return redirect(
            "teacher_academic_entry",
            class_id=classroom.id,
            subject_id=subject.id,
        )

    context = {
        "classroom": classroom,
        "subject": subject,
        "students": students,
        "pupils": students,
        "teacher": teacher,
    }

    return render(
        request,
        "teachersApp/academic.html",
        context,
    )

except Exception as exc:

    logger.exception(
        "CRITICAL ERROR in teacher_academic"
    )

    messages.error(
        request,
        f"An error occurred: {str(exc)}",
    )

    return redirect(
        "dashboard_final"
    )
```

# ============================================================

# BEHAVIOR

# ============================================================

@login_required
def teacher_behavior(
request,
pupil_id=None,
):

```
teacher = get_object_or_404(
    Teacher,
    user=request.user,
)

if pupil_id:

    pupil = get_object_or_404(
        Student,
        id=pupil_id,
    )

    if not teacher.assigned_class.filter(
        id=pupil.class_room_id
    ).exists():

        messages.error(
            request,
            "You are not assigned to this pupil's class.",
        )

        return redirect(
            "dashboard_final"
        )

    if request.method == "POST":

        category = request.POST.get(
            "category"
        )

        note = request.POST.get(
            "note"
        )

        conduct_remark = request.POST.get(
            "conduct_remark"
        )

        is_report_card_remark = (
            request.POST.get(
                "is_report_card_remark"
            )
            == "on"
        )

        if category and note:

            BehaviorLog.objects.create(
                pupil=pupil,
                teacher=teacher,
                category=category,
                note=note,
                conduct_remark=(
                    conduct_remark or ""
                ),
                is_report_card_remark=(
                    is_report_card_remark
                ),
            )

            messages.success(
                request,
                "Behavior log added.",
            )

            return redirect(
                "teacher_class_detail",
                class_id=pupil.class_room.id,
            )

        messages.error(
            request,
            "Please fill in all required fields.",
        )

    else:

        form = BehaviorLogForm(
            initial={
                "pupil": pupil
            }
        )

        if "pupil" in form.fields:
            form.fields[
                "pupil"
            ].widget = forms.HiddenInput()

    return render(
        request,
        "teachersApp/behavior_form.html",
        {
            "form": form,
            "pupil": pupil,
            "teacher": teacher,
        },
    )

logs = (
    BehaviorLog.objects
    .filter(teacher=teacher)
    .select_related("pupil")
    .order_by("-date")
)

return render(
    request,
    "teachersApp/behavior_list.html",
    {
        "logs": logs,
        "teacher": teacher,
    },
)
```

# ============================================================

# CLASS PERFORMANCE

# ============================================================

@login_required
def teacher_class_performance(
request,
class_id,
):

```
teacher = get_object_or_404(
    Teacher,
    user=request.user,
)

classroom = get_object_or_404(
    ClassRoom,
    id=class_id,
)

if not teacher.assigned_class.filter(
    id=classroom.id
).exists():

    messages.error(
        request,
        "You are not assigned to this class.",
    )

    return redirect(
        "dashboard_final"
    )

students = Student.objects.filter(
    class_room=classroom
)

school = getattr(
    request.user,
    "school",
    None,
)

if school is not None:
    students = students.filter(
        school=school
    )

subjects = teacher.subject.all()

performance_data = []

for student in students:

    row = {
        "student": student,
        "pupil": student,
    }

    total_marks = 0
    count = 0

    for subject in subjects:

        records = AcademicRecord.objects.filter(
            pupil=student,
            subject=subject,
            class_room=classroom,
        )

        avg = records.aggregate(
            Avg("marks")
        )["marks__avg"]

        row[subject.id] = (
            round(avg, 2)
            if avg is not None
            else "-"
        )

        if avg is not None:

            total_marks += avg
            count += 1

    row["average"] = (
        round(
            total_marks / count,
            2,
        )
        if count
        else "-"
    )

    performance_data.append(row)

context = {
    "classroom": classroom,
    "students": performance_data,
    "pupils": performance_data,
    "subjects": subjects,
    "teacher": teacher,
}

return render(
    request,
    "teachersApp/class_performance.html",
    context,
)
```

# ============================================================

# PRINT CLASS LIST

# ============================================================

@login_required
def teacher_print_class_list(
request,
class_id,
):

```
teacher = get_object_or_404(
    Teacher,
    user=request.user,
)

classroom = get_object_or_404(
    ClassRoom,
    id=class_id,
)

if not teacher.assigned_class.filter(
    id=classroom.id
).exists():

    messages.error(
        request,
        "You are not assigned to this class.",
    )

    return redirect(
        "dashboard_final"
    )

students = (
    Student.objects
    .filter(class_room=classroom)
    .select_related("user")
)

school = getattr(
    request.user,
    "school",
    None,
)

if school is not None:
    students = students.filter(
        school=school
    )

context = {
    "classroom": classroom,
    "students": students,
    "pupils": students,
    "teacher": teacher,
    "today": now().date(),
}

return render(
    request,
    "teachersApp/print_class_list.html",
    context,
)
```

# ============================================================

# PRINT RESULTS

# ============================================================

@login_required
def teacher_print_results(
request,
class_id,
subject_id,
):

```
teacher = get_object_or_404(
    Teacher,
    user=request.user,
)

classroom = get_object_or_404(
    ClassRoom,
    id=class_id,
)

subject = get_object_or_404(
    Subjects,
    id=subject_id,
)

if (
    not teacher.assigned_class.filter(
        id=classroom.id
    ).exists()
    or not teacher.subject.filter(
        id=subject.id
    ).exists()
):

    messages.error(
        request,
        "You are not assigned to this class or subject.",
    )

    return redirect(
        "dashboard_final"
    )

students = (
    Student.objects
    .filter(class_room=classroom)
    .select_related("user")
)

school = getattr(
    request.user,
    "school",
    None,
)

if school is not None:
    students = students.filter(
        school=school
    )

results = []

for student in students:

    records = AcademicRecord.objects.filter(
        pupil=student,
        subject=subject,
        class_room=classroom,
    )

    test = records.filter(
        exam_type="TEST"
    ).first()

    exam = records.filter(
        exam_type="EXAM"
    ).first()

    total = 0

    if test:
        total += test.marks

    if exam:
        total += exam.marks

    results.append(
        {
            "student": student,
            "pupil": student,
            "test": (
                test.marks
                if test
                else "-"
            ),
            "exam": (
                exam.marks
                if exam
                else "-"
            ),
            "total": (
                total
                if test or exam
                else "-"
            ),
        }
    )

context = {
    "classroom": classroom,
    "subject": subject,
    "results": results,
    "teacher": teacher,
    "today": now().date(),
}

return render(
    request,
    "teachersApp/print_results.html",
    context,
)
```

# ============================================================

# RESOURCES

# ============================================================

@login_required
def teacher_resources(request):

```
try:

    teacher = get_object_or_404(
        Teacher,
        user=request.user,
    )

    classes = teacher.assigned_class.all()

    resources = (
        Resource.objects
        .filter(
            class_room__in=classes
        )
        .select_related(
            "subject",
            "teacher",
        )
        .order_by("-created_at")
    )

    context = {
        "teacher": teacher,
        "resources": resources,
    }

    return render(
        request,
        "teachersApp/resources.html",
        context,
    )

except Exception:

    logger.exception(
        "Error in teacher_resources"
    )

    messages.error(
        request,
        "Could not load resources.",
    )

    return redirect(
        "dashboard_final"
    )
```

# ============================================================

# DEPLOYMENT TEST

# ============================================================

def final_test(request):
return HttpResponse(
"FINAL TEST WORKS! The new code is running."
)
