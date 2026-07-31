import datetime
import logging

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import DetailView, ListView, UpdateView

from accountsApp.mixins import AdminRequiredMixin
from accountsApp.models import Notice
from attendanceApp.models import Attendance
from classesApp.models import ClassRoom, Subjects
from examsApp.models import Exam
from resourcesApp.models import Resource
from studentsApp.models import Student

from .forms import (
    AssignmentForm,
    BehaviorLogForm,
    PupilReportForm,
    TeacherAdminForm,
)
from .models import (
    AcademicRecord,
    Assignment,
    BehaviorLog,
    PupilReport,
    Teacher,
    Timetable,
)

logger = logging.getLogger(__name__)


# ==========================================================
# ADMIN TEACHER VIEWS
# ==========================================================


class AdminTeacherList(AdminRequiredMixin, ListView):
    """
    Admin list of teachers.
    """

    model = Teacher
    template_name = "teachersApp/admin_teacher_list.html"
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            Teacher.objects.select_related("user", "user__school")
            .prefetch_related("subject", "assigned_class")
            .order_by("user__first_name", "user__last_name", "user__username")
        )

        query = self.request.GET.get("q", "").strip()

        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__username__icontains=query)
                | Q(subject__subject__icontains=query)
                | Q(assigned_class__name__icontains=query)
                | Q(assigned_class__section__icontains=query)
            ).distinct()

        return queryset


class AdminTeacherDetail(AdminRequiredMixin, DetailView):
    """
    Admin view of one teacher.
    """

    model = Teacher
    template_name = "teachersApp/admin_teacher_detail.html"

    def get_queryset(self):
        return (
            Teacher.objects.select_related("user", "user__school")
            .prefetch_related("subject", "assigned_class")
        )


class AdminTeacherUpdate(AdminRequiredMixin, UpdateView):
    """
    Admin edit view for a teacher profile.
    """

    model = Teacher
    form_class = TeacherAdminForm
    template_name = "teachersApp/admin_teacher_edit.html"

    def get_success_url(self):
        messages.success(self.request, "Teacher updated successfully.")

        return reverse_lazy(
            "admin_teacher_detail",
            kwargs={"pk": self.object.pk},
        )


# ==========================================================
# TEACHER DASHBOARD
# ==========================================================


@login_required
def dashboard_teacher(request):
    """
    Main teacher dashboard entry point.

    This intentionally redirects to dashboard_final because
    dashboard_final contains the actual teacher dashboard.
    """

    return redirect("dashboard_final")


@login_required
def dashboard_final(request):
    """
    Main Teacher Dashboard.

    IMPORTANT:
    ClassRoom currently DOES NOT contain a school field.

    Therefore we must NOT do:

        teacher.assigned_class.filter(school=school)

    or:

        teacher.assigned_class.all().filter(school=school)

    Teacher classes are determined from the Teacher.assigned_class
    ManyToMany relationship.

    Pupils DO contain a school field, so pupils can safely be
    restricted by the teacher's school.
    """

    try:
        # ------------------------------------------------------
        # Make sure the logged-in user actually has a teacher
        # profile.
        # ------------------------------------------------------

        teacher = get_object_or_404(
            Teacher.objects.select_related(
                "user",
                "user__school",
            ),
            user=request.user,
        )

        # ------------------------------------------------------
        # School belongs to the User model.
        # ------------------------------------------------------

        school = getattr(request.user, "school", None)

        # ------------------------------------------------------
        # TEACHER'S ASSIGNED CLASSES
        #
        # ClassRoom has:
        #   id
        #   name
        #   section
        #   capacity
        #
        # It does NOT have school.
        # ------------------------------------------------------

        assigned_classes = (
            teacher.assigned_class.all()
            .order_by("name", "section")
        )

        # ------------------------------------------------------
        # TEACHER'S ASSIGNED SUBJECTS
        #
        # Subjects uses the field:
        #
        #     subject
        #
        # not:
        #
        #     name
        # ------------------------------------------------------

        assigned_subjects = (
            teacher.subject.all()
            .order_by("subject")
        )

        # ------------------------------------------------------
        # PUPILS
        #
        # Student is internally the Django model name, but the
        # user-facing terminology remains Pupil/Pupils.
        #
        # Student DOES have a school field.
        # ------------------------------------------------------

        pupils_queryset = Student.objects.filter(
            class_room__in=assigned_classes,
        ).select_related(
            "user",
            "school",
            "class_room",
        )

        if school is not None:
            pupils_queryset = pupils_queryset.filter(
                school=school
            )

        pupils = pupils_queryset

        # ------------------------------------------------------
        # UPCOMING EXAMS
        # ------------------------------------------------------

        upcoming_exams = (
            Exam.objects.filter(
                class_room__in=assigned_classes,
            )
            .select_related(
                "subject",
                "class_room",
            )
            .order_by("exam_date")
        )

        # ------------------------------------------------------
        # SCHOOL NOTICES
        #
        # Notice -> created_by -> school is valid because User
        # contains the school ForeignKey.
        # ------------------------------------------------------

        if school is not None:
            notices = (
                Notice.objects.filter(
                    created_by__school=school,
                )
                .select_related("created_by")
                .order_by("-created_at")[:8]
            )
        else:
            notices = (
                Notice.objects.filter(
                    created_by=request.user,
                )
                .select_related("created_by")
                .order_by("-created_at")[:8]
            )

        # ------------------------------------------------------
        # TEACHER ASSIGNMENTS
        # ------------------------------------------------------

        assignments = (
            Assignment.objects.filter(
                teacher=teacher,
            )
            .select_related(
                "subject",
                "class_room",
                "teacher",
            )
            .order_by("-created_at")[:5]
        )

        # ------------------------------------------------------
        # TEACHER TIMETABLE
        # ------------------------------------------------------

        timetable_today = (
            Timetable.objects.filter(
                teacher=teacher,
            )
            .select_related(
                "class_room",
                "subject",
            )
            .order_by("day", "start_time")
        )

        # ------------------------------------------------------
        # DASHBOARD CONTEXT
        # ------------------------------------------------------

        context = {
            "teacher": teacher,
            "school": school,
            "classes": assigned_classes,
            "subjects": assigned_subjects,
            "exams": upcoming_exams[:6],
            "assignments": assignments,
            "today_timetable": timetable_today,
            "notices": notices,
            "stats": {
                "classes": assigned_classes.count(),
                "subjects": assigned_subjects.count(),
                "students": pupils.count(),
                "upcoming_exams": upcoming_exams.count(),
            },
        }

        return render(
            request,
            "teachersApp/dashboard_final.html",
            context,
        )

    except Teacher.DoesNotExist:
        logger.exception(
            "Teacher profile does not exist for user %s.",
            request.user.pk,
        )

        messages.error(
            request,
            "Your teacher profile could not be found. "
            "Please contact the school administrator.",
        )

        return redirect("home")

    except Exception:
        logger.exception(
            "Unable to load teacher dashboard for user %s.",
            request.user.pk,
        )

        messages.error(
            request,
            "Unable to load your teacher dashboard.",
        )

        return redirect("home")


# ==========================================================
# TEACHER CLASS DETAIL / ATTENDANCE
# ==========================================================


@login_required
def teacher_class_detail(request, class_id):
    """
    Displays a teacher's assigned class and allows attendance
    to be recorded for its pupils.
    """

    try:
        teacher = get_object_or_404(
            Teacher.objects.select_related(
                "user",
                "user__school",
            ),
            user=request.user,
        )

        classroom = get_object_or_404(
            ClassRoom,
            id=class_id,
        )

        # ------------------------------------------------------
        # SECURITY:
        # Teacher may only access assigned classes.
        # ------------------------------------------------------

        if not teacher.assigned_class.filter(
            id=classroom.id
        ).exists():
            messages.error(
                request,
                "You are not assigned to this class.",
            )

            return redirect("dashboard_final")

        # ------------------------------------------------------
        # PUPILS IN THIS CLASS
        # ------------------------------------------------------

        students = (
            Student.objects.filter(
                class_room=classroom,
            )
            .select_related(
                "user",
                "school",
                "parent",
                "parent__user",
            )
            .order_by(
                "user__first_name",
                "user__last_name",
                "user__username",
            )
        )

        # ------------------------------------------------------
        # POST = SAVE ATTENDANCE
        # ------------------------------------------------------

        if request.method == "POST":

            today = now().date()

            for student in students:

                status = request.POST.get(
                    f"status_{student.id}"
                )

                if status in {
                    "present",
                    "absent",
                    "late",
                }:

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
                "Attendance saved successfully.",
            )

            return redirect(
                "teacher_class_detail",
                class_id=classroom.id,
            )

        # ------------------------------------------------------
        # TODAY'S ATTENDANCE
        # ------------------------------------------------------

        today = now().date()

        attendance_records = Attendance.objects.filter(
            student__in=students,
            date=today,
        )

        attendance_map = {
            record.student_id: record.status
            for record in attendance_records
        }

        # ------------------------------------------------------
        # PREPARE PUPIL DATA
        # ------------------------------------------------------

        pupil_data = []

        for pupil in students:

            parent_user = None

            if pupil.parent_id and pupil.parent.user_id:
                parent_user = pupil.parent.user

            pupil_data.append(
                {
                    "student": pupil,
                    "pupil": pupil,
                    "today_status": attendance_map.get(
                        pupil.id,
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
                "student_data": pupil_data,
                "pupil_data": pupil_data,
                "students": students,
                "pupils": students,
                "today": today,
                "teacher": teacher,
            },
        )

    except Exception:
        logger.exception(
            "Error in teacher_class_detail. "
            "class_id=%s user=%s",
            class_id,
            request.user.pk,
        )

        messages.error(
            request,
            "Unable to load this class.",
        )

        return redirect("dashboard_final")


# ==========================================================
# PUPIL REPORT
# ==========================================================


@login_required
def pupil_report_create_or_edit(
    request,
    pupil_id,
    term=None,
    year=None,
):
    """
    Create or edit a pupil report for a pupil belonging to
    one of the teacher's assigned classes.
    """

    try:
        teacher = get_object_or_404(
            Teacher,
            user=request.user,
        )

        pupil = get_object_or_404(
            Student.objects.select_related(
                "user",
                "school",
                "class_room",
            ),
            id=pupil_id,
        )

        # ------------------------------------------------------
        # SECURITY
        # ------------------------------------------------------

        if (
            not pupil.class_room_id
            or not teacher.assigned_class.filter(
                id=pupil.class_room_id
            ).exists()
        ):
            messages.error(
                request,
                "You are not allowed to report on this pupil.",
            )

            return redirect("dashboard_final")

        # ------------------------------------------------------
        # DEFAULT TERM
        # ------------------------------------------------------

        if term is None:
            term = "1"

        # ------------------------------------------------------
        # DEFAULT ACADEMIC YEAR
        # ------------------------------------------------------

        if year is None:

            current_year = datetime.date.today().year

            year = (
                f"{current_year}/"
                f"{current_year + 1}"
            )

        # ------------------------------------------------------
        # GET OR CREATE REPORT
        # ------------------------------------------------------

        report, created = PupilReport.objects.get_or_create(
            pupil=pupil,
            term=term,
            academic_year=year,
            defaults={
                "teacher": teacher,
            },
        )

        # ------------------------------------------------------
        # POST
        # ------------------------------------------------------

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
                    (
                        f"Report for "
                        f"{pupil.user.get_full_name() or pupil.user.username} "
                        f"saved successfully."
                    ),
                )

                if report.is_submitted:

                    messages.info(
                        request,
                        "The report has been submitted.",
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
                instance=report,
            )

        return render(
            request,
            "teachersApp/report_form.html",
            {
                "form": form,
                "pupil": pupil,
                "report": report,
                "classroom": pupil.class_room,
                "teacher": teacher,
            },
        )

    except Exception:
        logger.exception(
            "Error in pupil_report_create_or_edit. "
            "pupil_id=%s user=%s",
            pupil_id,
            request.user.pk,
        )

        messages.error(
            request,
            "Unable to save the pupil report.",
        )

        return redirect("dashboard_final")


# ==========================================================
# TEACHER TIMETABLE
# ==========================================================


@login_required
def teacher_timetable(request):
    """
    Display the teacher timetable grouped by day.
    """

    try:

        teacher = get_object_or_404(
            Teacher,
            user=request.user,
        )

        timetable_entries = (
            Timetable.objects.filter(
                teacher=teacher,
            )
            .select_related(
                "class_room",
                "subject",
            )
            .order_by(
                "day",
                "start_time",
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
                timetable[entry.day].append(
                    entry
                )

        return render(
            request,
            "teachersApp/timetable.html",
            {
                "teacher": teacher,
                "timetable": timetable,
                "days": days,
            },
        )

    except Exception:
        logger.exception(
            "Error loading teacher timetable for user %s.",
            request.user.pk,
        )

        messages.error(
            request,
            "Unable to load your timetable.",
        )

        return redirect("dashboard_final")


# ==========================================================
# TEACHER ASSIGNMENTS
# ==========================================================


@login_required
def teacher_assignments(request):
    """
    Display assignments created by the logged-in teacher.
    """

    teacher = get_object_or_404(
        Teacher,
        user=request.user,
    )

    assignments = (
        Assignment.objects.filter(
            teacher=teacher,
        )
        .select_related(
            "subject",
            "class_room",
            "teacher",
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


@login_required
def teacher_assignment_create(request):
    """
    Create an assignment.

    The teacher can only select:
        - their assigned classes
        - their assigned subjects
    """

    teacher = get_object_or_404(
        Teacher,
        user=request.user,
    )

    if request.method == "POST":

        form = AssignmentForm(
            request.POST,
            request.FILES,
        )

        # Restrict POST form choices as well.
        form.fields["class_room"].queryset = (
            teacher.assigned_class.all()
        )

        form.fields["subject"].queryset = (
            teacher.subject.all()
        )

        form.instance.teacher = teacher

        if form.is_valid():

            assignment = form.save(
                commit=False
            )

            assignment.teacher = teacher

            assignment.save()

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


# ==========================================================
# ACADEMIC RECORDS
# ==========================================================


@login_required
def teacher_academic(
    request,
    class_id=None,
    subject_id=None,
):
    """
    Teacher academic marks entry.

    Teachers can only enter marks for:
        - assigned classes
        - assigned subjects
    """

    try:

        teacher = get_object_or_404(
            Teacher,
            user=request.user,
        )

        # ------------------------------------------------------
        # Read IDs from query string if they were not supplied
        # by the URL.
        # ------------------------------------------------------

        if not class_id or class_id == 0:
            class_id = request.GET.get(
                "class_id"
            )

        if not subject_id or subject_id == 0:
            subject_id = request.GET.get(
                "subject_id"
            )

        # ------------------------------------------------------
        # Convert IDs safely.
        # ------------------------------------------------------

        try:

            if class_id:
                class_id = int(class_id)

            if subject_id:
                subject_id = int(subject_id)

        except (TypeError, ValueError):

            messages.error(
                request,
                "Invalid class or subject.",
            )

            return redirect(
                "dashboard_final"
            )

        # ------------------------------------------------------
        # SELECTION PAGE
        # ------------------------------------------------------

        if not class_id or not subject_id:

            classes = (
                teacher.assigned_class.all()
                .order_by(
                    "name",
                    "section",
                )
            )

            subjects = (
                teacher.subject.all()
                .order_by("subject")
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

        # ------------------------------------------------------
        # GET CLASS AND SUBJECT
        # ------------------------------------------------------

        classroom = get_object_or_404(
            ClassRoom,
            id=class_id,
        )

        subject = get_object_or_404(
            Subjects,
            id=subject_id,
        )

        # ------------------------------------------------------
        # SECURITY
        # ------------------------------------------------------

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

        if not teacher.subject.filter(
            id=subject.id
        ).exists():

            messages.error(
                request,
                "You are not assigned to this subject.",
            )

            return redirect(
                "dashboard_final"
            )

        # ------------------------------------------------------
        # PUPILS
        # ------------------------------------------------------

        students = (
            Student.objects.filter(
                class_room=classroom,
            )
            .select_related(
                "user",
                "school",
            )
            .order_by(
                "user__first_name",
                "user__last_name",
                "user__username",
            )
        )

        # ------------------------------------------------------
        # SAVE MARKS
        # ------------------------------------------------------

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
                    (
                        "Please select a term "
                        "and enter an academic year."
                    ),
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

                test_max_marks = request.POST.get(
                    f"test_max_marks_{student.id}"
                )

                exam_max_marks = request.POST.get(
                    f"exam_max_marks_{student.id}"
                )

                # --------------------------------------------------
                # TEST
                # --------------------------------------------------

                if (
                    test_marks
                    and test_marks.strip()
                ):

                    try:

                        marks = float(
                            test_marks
                        )

                        max_marks = (
                            float(test_max_marks)
                            if test_max_marks
                            else 30
                        )

                        AcademicRecord.objects.create(
                            pupil=student,
                            subject=subject,
                            class_room=classroom,
                            term=term,
                            academic_year=academic_year,
                            exam_type="TEST",
                            marks=marks,
                            max_marks=max_marks,
                            teacher=teacher,
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        logger.warning(
                            "Invalid TEST marks for pupil %s.",
                            student.id,
                        )

                # --------------------------------------------------
                # EXAM
                # --------------------------------------------------

                if (
                    exam_marks
                    and exam_marks.strip()
                ):

                    try:

                        marks = float(
                            exam_marks
                        )

                        max_marks = (
                            float(exam_max_marks)
                            if exam_max_marks
                            else 50
                        )

                        AcademicRecord.objects.create(
                            pupil=student,
                            subject=subject,
                            class_room=classroom,
                            term=term,
                            academic_year=academic_year,
                            exam_type="EXAM",
                            marks=marks,
                            max_marks=max_marks,
                            teacher=teacher,
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        logger.warning(
                            "Invalid EXAM marks for pupil %s.",
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

        return render(
            request,
            "teachersApp/academic.html",
            {
                "classroom": classroom,
                "subject": subject,
                "students": students,
                "pupils": students,
                "teacher": teacher,
            },
        )

    except Exception:
        logger.exception(
            "Critical error in teacher_academic. "
            "class_id=%s subject_id=%s user=%s",
            class_id,
            subject_id,
            request.user.pk,
        )

        messages.error(
            request,
            "Unable to load the academic records page.",
        )

        return redirect(
            "dashboard_final"
        )


# ==========================================================
# BEHAVIOR
# ==========================================================


@login_required
def teacher_behavior(
    request,
    pupil_id=None,
):
    """
    Add or list teacher behavior records.
    """

    teacher = get_object_or_404(
        Teacher,
        user=request.user,
    )

    if pupil_id:

        pupil = get_object_or_404(
            Student.objects.select_related(
                "user",
                "class_room",
                "school",
            ),
            id=pupil_id,
        )

        if (
            not pupil.class_room_id
            or not teacher.assigned_class.filter(
                id=pupil.class_room_id
            ).exists()
        ):

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
                    "Behavior log added successfully.",
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

    # ------------------------------------------------------
    # LIST BEHAVIOR LOGS
    # ------------------------------------------------------

    logs = (
        BehaviorLog.objects.filter(
            teacher=teacher,
        )
        .select_related(
            "pupil",
            "pupil__user",
        )
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


# ==========================================================
# CLASS PERFORMANCE
# ==========================================================


@login_required
def teacher_class_performance(
    request,
    class_id,
):
    """
    Display academic performance of pupils in a teacher's
    assigned class.
    """

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
        Student.objects.filter(
            class_room=classroom,
        )
        .select_related(
            "user",
            "school",
        )
    )

    subjects = (
        teacher.subject.all()
        .order_by("subject")
    )

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

            average = records.aggregate(
                Avg("marks")
            )["marks__avg"]

            row[subject.id] = (
                round(average, 2)
                if average is not None
                else "-"
            )

            if average is not None:

                total_marks += average
                count += 1

        row["average"] = (
            round(
                total_marks / count,
                2,
            )
            if count
            else "-"
        )

        performance_data.append(
            row
        )

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


# ==========================================================
# PRINT CLASS LIST
# ==========================================================


@login_required
def teacher_print_class_list(
    request,
    class_id,
):
    """
    Printable pupil list for an assigned class.
    """

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
        Student.objects.filter(
            class_room=classroom,
        )
        .select_related(
            "user",
            "school",
        )
        .order_by(
            "user__first_name",
            "user__last_name",
            "user__username",
        )
    )

    return render(
        request,
        "teachersApp/print_class_list.html",
        {
            "classroom": classroom,
            "students": students,
            "pupils": students,
            "teacher": teacher,
            "today": now().date(),
        },
    )


# ==========================================================
# PRINT RESULTS
# ==========================================================


@login_required
def teacher_print_results(
    request,
    class_id,
    subject_id,
):
    """
    Printable results for a teacher's assigned class and
    subject.
    """

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

    if not teacher.subject.filter(
        id=subject.id
    ).exists():

        messages.error(
            request,
            "You are not assigned to this subject.",
        )

        return redirect(
            "dashboard_final"
        )

    students = (
        Student.objects.filter(
            class_room=classroom,
        )
        .select_related(
            "user",
            "school",
        )
        .order_by(
            "user__first_name",
            "user__last_name",
            "user__username",
        )
    )

    results = []

    for student in students:

        records = (
            AcademicRecord.objects.filter(
                pupil=student,
                subject=subject,
                class_room=classroom,
            )
            .order_by("-date_recorded")
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

    return render(
        request,
        "teachersApp/print_results.html",
        {
            "classroom": classroom,
            "subject": subject,
            "results": results,
            "teacher": teacher,
            "today": now().date(),
        },
    )


# ==========================================================
# TEACHER RESOURCES
# ==========================================================


@login_required
def teacher_resources(request):
    """
    Display resources belonging to the teacher's assigned
    classes.

    IMPORTANT:
    Resource uses `uploaded_by`, not `teacher`.
    """

    try:

        teacher = get_object_or_404(
            Teacher,
            user=request.user,
        )

        classes = teacher.assigned_class.all()

        resources = (
            Resource.objects.filter(
                class_room__in=classes,
            )
            .select_related(
                "subject",
                "class_room",
                "uploaded_by",
            )
            .order_by("-created_at")
        )

        return render(
            request,
            "teachersApp/resources.html",
            {
                "teacher": teacher,
                "resources": resources,
            },
        )

    except Exception:
        logger.exception(
            "Error loading teacher resources for user %s.",
            request.user.pk,
        )

        messages.error(
            request,
            "Could not load resources.",
        )

        return redirect(
            "dashboard_final"
        )


# ==========================================================
# DEVELOPMENT TEST
# ==========================================================


def final_test(request):
    """
    Simple development endpoint used to confirm that the
    current teacher views.py file is loaded.
    """

    return HttpResponse(
        "FINAL TEST WORKS! The new teacher views.py is running."
    )