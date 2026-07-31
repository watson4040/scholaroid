
# ============================================================
# teachersApp/views.py
# ============================================================

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from accountsApp.models import User
from classesApp.models import ClassRoom, Subjects
from examsApp.models import Exam
from studentsApp.models import Student

from .models import (
    AcademicRecord,
    Assignment,
    BehaviorLog,
    PupilReport,
    Teacher,
    Timetable,
)

logger = logging.getLogger(__name__)


# ============================================================
# HELPER: GET CURRENT TEACHER
# ============================================================

def get_teacher(request):
    """
    Return the Teacher profile belonging to the logged-in user.

    If the account is not a teacher, return 403.
    """

    if not request.user.is_authenticated:
        return None

    teacher = get_object_or_404(
        Teacher.objects.select_related("user"),
        user=request.user,
    )

    return teacher


# ============================================================
# HELPER: GET TEACHER SCHOOL
# ============================================================

def get_teacher_school(request):
    """
    Get the school assigned to the logged-in teacher.

    The school belongs to User, not ClassRoom.
    """

    if not request.user.is_authenticated:
        return None

    return getattr(
        request.user,
        "school",
        None,
    )


# ============================================================
# HELPER: GET TEACHER CLASSES
# ============================================================

def get_teacher_classes(teacher):
    """
    Return only classes assigned to the teacher.

    IMPORTANT:
    ClassRoom does NOT have a school field.

    Therefore DO NOT do:

        teacher.assigned_class.filter(school=school)

    School isolation is handled through the pupils' school
    instead.
    """

    return (
        teacher.assigned_class
        .all()
        .order_by(
            "name",
            "section",
        )
    )


# ============================================================
# HELPER: TEACHER CLASS ACCESS
# ============================================================

def teacher_has_access_to_class(
    teacher,
    class_room,
):
    """
    Check whether the teacher is assigned to this class.
    """

    if teacher is None or class_room is None:
        return False

    return teacher.assigned_class.filter(
        pk=class_room.pk
    ).exists()


# ============================================================
# HELPER: TEACHER SUBJECT ACCESS
# ============================================================

def teacher_has_access_to_subject(
    teacher,
    subject,
):
    """
    Check whether the teacher teaches this subject.
    """

    if teacher is None or subject is None:
        return False

    return teacher.subject.filter(
        pk=subject.pk
    ).exists()


# ============================================================
# HELPER: FILTER PUPILS BY TEACHER SCHOOL
# ============================================================

def get_teacher_pupils(
    request,
    queryset=None,
):
    """
    Return pupils belonging to the teacher's assigned classes.

    School filtering is performed on Student.school because
    Student has a school ForeignKey.

    ClassRoom does NOT have a school field.
    """

    teacher = get_teacher(request)

    if queryset is None:
        classes = get_teacher_classes(teacher)

        pupils = (
            Student.objects
            .filter(
                class_room__in=classes
            )
        )

    else:
        pupils = queryset

    pupils = (
        pupils
        .select_related(
            "user",
            "class_room",
            "school",
        )
        .order_by(
            "user__first_name",
            "user__last_name",
        )
    )

    school = get_teacher_school(request)

    if school is not None:
        pupils = pupils.filter(
            school=school
        )

    return pupils


# ============================================================
# TEACHER DASHBOARD
# ============================================================

@login_required
def dashboard_teacher(request):

    teacher = get_teacher(request)

    school = get_teacher_school(request)

    classes = get_teacher_classes(
        teacher
    )

    subjects = (
        teacher.subject
        .all()
        .order_by("subject")
    )

    pupils = get_teacher_pupils(
        request
    )

    exams = (
        Exam.objects
        .filter(
            class_room__in=classes
        )
        .select_related(
            "subject",
            "class_room",
        )
        .order_by(
            "exam_date"
        )
    )

    assignments = (
        Assignment.objects
        .filter(
            teacher=teacher
        )
        .select_related(
            "subject",
            "class_room",
        )
        .order_by(
            "-created_at"
        )[:10]
    )

    timetable = (
        Timetable.objects
        .filter(
            teacher=teacher
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

    context = {
        "teacher": teacher,
        "school": school,

        "classes": classes,
        "subjects": subjects,

        "pupils": pupils[:20],
        "students": pupils[:20],

        "exams": exams[:10],

        "assignments": assignments,

        "today_timetable": timetable,
        "timetable": timetable,

        "stats": {
            "classes": classes.count(),
            "subjects": subjects.count(),
            "students": pupils.count(),
            "pupils": pupils.count(),
            "upcoming_exams": exams.count(),
        },
    }

    return render(
        request,
        "teachersApp/dashboard_final.html",
        context,
    )


# ============================================================
# DASHBOARD ALIAS
# ============================================================

@login_required
def dashboard_final(request):
    """
    Final teacher dashboard.

    This is kept separate because teachersApp/urls.py points
    the /final/ route to dashboard_final.
    """

    teacher = get_teacher(request)

    school = get_teacher_school(request)

    classes = get_teacher_classes(
        teacher
    )

    subjects = (
        teacher.subject
        .all()
        .order_by("subject")
    )

    pupils = get_teacher_pupils(
        request
    )

    exams = (
        Exam.objects
        .filter(
            class_room__in=classes
        )
        .select_related(
            "subject",
            "class_room",
        )
        .order_by(
            "exam_date"
        )
    )

    assignments = (
        Assignment.objects
        .filter(
            teacher=teacher
        )
        .select_related(
            "subject",
            "class_room",
        )
        .order_by(
            "-created_at"
        )[:10]
    )

    timetable = (
        Timetable.objects
        .filter(
            teacher=teacher
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

    context = {
        "teacher": teacher,
        "school": school,

        "classes": classes,
        "subjects": subjects,

        "pupils": pupils[:20],
        "students": pupils[:20],

        "exams": exams[:10],

        "assignments": assignments,

        "today_timetable": timetable,
        "timetable": timetable,

        "stats": {
            "classes": classes.count(),
            "subjects": subjects.count(),
            "students": pupils.count(),
            "pupils": pupils.count(),
            "upcoming_exams": exams.count(),
        },
    }

    return render(
        request,
        "teachersApp/dashboard_final.html",
        context,
    )


# ============================================================
# TEACHER CLASS DETAIL
# ============================================================

@login_required
def teacher_class_detail(
    request,
    class_id,
):

    teacher = get_teacher(request)

    class_room = get_object_or_404(
        ClassRoom,
        pk=class_id,
    )

    if not teacher_has_access_to_class(
        teacher,
        class_room,
    ):
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    school = get_teacher_school(request)

    pupils = (
        Student.objects
        .filter(
            class_room=class_room
        )
        .select_related(
            "user",
            "class_room",
            "school",
        )
        .order_by(
            "user__first_name",
            "user__last_name",
        )
    )

    # IMPORTANT:
    # Student has school, so filtering here is valid.
    if school is not None:
        pupils = pupils.filter(
            school=school
        )

    subjects = (
        teacher.subject
        .all()
        .order_by(
            "subject"
        )
    )

    exams = (
        Exam.objects
        .filter(
            class_room=class_room
        )
        .select_related(
            "subject"
        )
        .order_by(
            "exam_date"
        )
    )

    assignments = (
        Assignment.objects
        .filter(
            teacher=teacher,
            class_room=class_room,
        )
        .select_related(
            "subject",
        )
        .order_by(
            "-created_at"
        )
    )

    academic_records = (
        AcademicRecord.objects
        .filter(
            teacher=teacher,
            class_room=class_room,
        )
        .select_related(
            "pupil",
            "pupil__user",
            "subject",
        )
        .order_by(
            "-date_recorded"
        )
    )

    context = {
        "teacher": teacher,
        "school": school,

        "class_room": class_room,
        "class": class_room,

        "pupils": pupils,
        "students": pupils,

        "subjects": subjects,
        "exams": exams,

        "assignments": assignments,

        "academic_records": academic_records,
    }

    return render(
        request,
        "teachersApp/class_detail.html",
        context,
    )


# ============================================================
# PUPIL REPORT CREATE / EDIT
# ============================================================

@login_required
def pupil_report_create_or_edit(
    request,
    pupil_id,
):

    teacher = get_teacher(request)

    school = get_teacher_school(request)

    pupil = get_object_or_404(
        Student.objects.select_related(
            "user",
            "class_room",
            "school",
        ),
        pk=pupil_id,
    )

    # --------------------------------------------------------
    # SCHOOL SECURITY
    # --------------------------------------------------------

    if (
        school is not None
        and pupil.school_id != school.id
    ):
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    # --------------------------------------------------------
    # CLASS SECURITY
    # --------------------------------------------------------

    if (
        pupil.class_room_id
        and not teacher.assigned_class.filter(
            pk=pupil.class_room_id
        ).exists()
    ):
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    term = request.POST.get(
        "term",
        request.GET.get(
            "term",
            "1",
        ),
    )

    academic_year = request.POST.get(
        "academic_year",
        request.GET.get(
            "academic_year",
            "",
        ),
    ).strip()

    report = None

    if academic_year:

        report = (
            PupilReport.objects
            .filter(
                pupil=pupil,
                term=term,
                academic_year=academic_year,
            )
            .first()
        )

    if request.method == "POST":

        comment = request.POST.get(
            "comment",
            "",
        ).strip()

        is_submitted = (
            request.POST.get(
                "is_submitted"
            )
            in [
                "1",
                "true",
                "True",
                "on",
                "yes",
            ]
        )

        if not academic_year:

            messages.error(
                request,
                "Academic year is required.",
            )

        else:

            if report is None:

                report = PupilReport.objects.create(
                    pupil=pupil,
                    term=term,
                    academic_year=academic_year,
                    teacher=teacher,
                    comment=comment,
                    is_submitted=is_submitted,
                )

            else:

                report.teacher = teacher
                report.comment = comment
                report.is_submitted = is_submitted

                report.save()

            messages.success(
                request,
                "Pupil report saved successfully.",
            )

            return redirect(
                "teacher_class_detail",
                class_id=pupil.class_room_id,
            )

    context = {
        "teacher": teacher,
        "school": school,

        "pupil": pupil,
        "student": pupil,

        "report": report,

        "term": term,
        "academic_year": academic_year,

        "term_choices": PupilReport.TERM_CHOICES,
    }

    return render(
        request,
        "teachersApp/pupil_report.html",
        context,
    )

# ============================================================
# TEACHER TIMETABLE
# ============================================================

@login_required
def teacher_timetable(request):

    teacher = get_teacher(request)

    timetable = (
        Timetable.objects
        .filter(
            teacher=teacher
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

    context = {
        "teacher": teacher,
        "timetable": timetable,
        "today_timetable": timetable,
    }

    return render(
        request,
        "teachersApp/timetable.html",
        context,
    )


# ============================================================
# TEACHER ASSIGNMENTS
# ============================================================

@login_required
def teacher_assignments(request):

    teacher = get_teacher(request)

    assignments = (
        Assignment.objects
        .filter(
            teacher=teacher
        )
        .select_related(
            "subject",
            "class_room",
        )
        .order_by(
            "-created_at"
        )
    )

    context = {
        "teacher": teacher,
        "assignments": assignments,
        "classes": get_teacher_classes(teacher),
        "subjects": teacher.subject.all(),
    }

    return render(
        request,
        "teachersApp/assignments.html",
        context,
    )


# ============================================================
# CREATE ASSIGNMENT
# ============================================================

@login_required
def teacher_assignment_create(request):

    teacher = get_teacher(request)

    classes = get_teacher_classes(
        teacher
    )

    subjects = teacher.subject.all()

    if request.method == "POST":

        title = request.POST.get(
            "title",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        subject_id = request.POST.get(
            "subject"
        )

        class_id = request.POST.get(
            "class_room"
        )

        due_date = request.POST.get(
            "due_date"
        )

        file_upload = request.FILES.get(
            "file_upload"
        )

        if not title:

            messages.error(
                request,
                "Assignment title is required.",
            )

        elif not description:

            messages.error(
                request,
                "Assignment description is required.",
            )

        elif not subject_id:

            messages.error(
                request,
                "Please select a subject.",
            )

        elif not class_id:

            messages.error(
                request,
                "Please select a class.",
            )

        elif not due_date:

            messages.error(
                request,
                "Please select a due date.",
            )

        else:

            subject = get_object_or_404(
                Subjects,
                pk=subject_id,
            )

            class_room = get_object_or_404(
                ClassRoom,
                pk=class_id,
            )

            if not teacher_has_access_to_subject(
                teacher,
                subject,
            ):
                return render(
                    request,
                    "errors/403.html",
                    status=403,
                )

            if not teacher_has_access_to_class(
                teacher,
                class_room,
            ):
                return render(
                    request,
                    "errors/403.html",
                    status=403,
                )

            Assignment.objects.create(
                title=title,
                description=description,
                subject=subject,
                class_room=class_room,
                teacher=teacher,
                due_date=due_date,
                file_upload=file_upload,
            )

            messages.success(
                request,
                "Assignment created successfully.",
            )

            return redirect(
                "teacher_assignments"
            )

    context = {
        "teacher": teacher,
        "classes": classes,
        "subjects": subjects,
    }

    return render(
        request,
        "teachersApp/assignment_form.html",
        context,
    )


# ============================================================
# TEACHER ACADEMIC
# ============================================================

@login_required
def teacher_academic(
    request,
    class_id=None,
    subject_id=None,
):

    teacher = get_teacher(request)

    classes = get_teacher_classes(
        teacher
    )

    subjects = teacher.subject.all()

    selected_class = None
    selected_subject = None

    # --------------------------------------------------------
    # CLASS
    # --------------------------------------------------------

    if class_id is not None:

        selected_class = get_object_or_404(
            ClassRoom,
            pk=class_id,
        )

        if not teacher_has_access_to_class(
            teacher,
            selected_class,
        ):
            return render(
                request,
                "errors/403.html",
                status=403,
            )

    # --------------------------------------------------------
    # SUBJECT
    # --------------------------------------------------------

    if subject_id is not None:

        selected_subject = get_object_or_404(
            Subjects,
            pk=subject_id,
        )

        if not teacher_has_access_to_subject(
            teacher,
            selected_subject,
        ):
            return render(
                request,
                "errors/403.html",
                status=403,
            )

    # --------------------------------------------------------
    # PUPILS
    # --------------------------------------------------------

    pupils = Student.objects.none()

    if selected_class:

        pupils = (
            Student.objects
            .filter(
                class_room=selected_class
            )
            .select_related(
                "user",
                "class_room",
                "school",
            )
            .order_by(
                "user__first_name",
                "user__last_name",
            )
        )

        school = get_teacher_school(request)

        if school is not None:

            pupils = pupils.filter(
                school=school
            )

    # --------------------------------------------------------
    # RECORDS
    # --------------------------------------------------------

    records = AcademicRecord.objects.none()

    if selected_class:

        records = (
            AcademicRecord.objects
            .filter(
                teacher=teacher,
                class_room=selected_class,
            )
            .select_related(
                "pupil",
                "pupil__user",
                "subject",
            )
            .order_by(
                "-date_recorded"
            )
        )

        if selected_subject:

            records = records.filter(
                subject=selected_subject
            )

    # --------------------------------------------------------
    # SAVE MARKS
    # --------------------------------------------------------

    if request.method == "POST":

        pupil_id = request.POST.get(
            "pupil_id"
        )

        subject_post_id = request.POST.get(
            "subject_id",
            subject_id,
        )

        class_post_id = request.POST.get(
            "class_id",
            class_id,
        )

        marks = request.POST.get(
            "marks"
        )

        max_marks = request.POST.get(
            "max_marks",
            "100",
        )

        term = request.POST.get(
            "term",
            "1",
        )

        academic_year = request.POST.get(
            "academic_year",
            "",
        ).strip()

        exam_type = request.POST.get(
            "exam_type",
            "TEST",
        )

        remark = request.POST.get(
            "remark",
            "",
        ).strip()

        if (
            pupil_id
            and subject_post_id
            and class_post_id
            and marks
            and academic_year
        ):

            pupil = get_object_or_404(
                Student,
                pk=pupil_id,
            )

            subject = get_object_or_404(
                Subjects,
                pk=subject_post_id,
            )

            class_room = get_object_or_404(
                ClassRoom,
                pk=class_post_id,
            )

            if not teacher_has_access_to_class(
                teacher,
                class_room,
            ):
                return render(
                    request,
                    "errors/403.html",
                    status=403,
                )

            if not teacher_has_access_to_subject(
                teacher,
                subject,
            ):
                return render(
                    request,
                    "errors/403.html",
                    status=403,
                )

            # Ensure pupil belongs to this class.
            if pupil.class_room_id != class_room.pk:
                return render(
                    request,
                    "errors/403.html",
                    status=403,
                )

            school = get_teacher_school(request)

            if (
                school is not None
                and pupil.school_id != school.id
            ):
                return render(
                    request,
                    "errors/403.html",
                    status=403,
                )

            AcademicRecord.objects.create(
                pupil=pupil,
                subject=subject,
                class_room=class_room,
                term=term,
                academic_year=academic_year,
                exam_type=exam_type,
                marks=marks,
                max_marks=max_marks,
                remark=remark,
                teacher=teacher,
            )

            messages.success(
                request,
                "Academic record saved successfully.",
            )

            return redirect(
                "teacher_academic_entry",
                class_id=class_room.pk,
                subject_id=subject.pk,
            )

        messages.error(
            request,
            "Please complete all required academic record fields.",
        )

    context = {
        "teacher": teacher,
        "classes": classes,
        "subjects": subjects,

        "selected_class": selected_class,
        "selected_subject": selected_subject,

        "pupils": pupils,
        "students": pupils,

        "records": records,
        "academic_records": records,

        "exam_types": AcademicRecord.EXAM_TYPES,
        "term_choices": PupilReport.TERM_CHOICES,
    }

    return render(
        request,
        "teachersApp/academic.html",
        context,
    )


# ============================================================
# TEACHER BEHAVIOR
# ============================================================

@login_required
def teacher_behavior(
    request,
    pupil_id=None,
):

    teacher = get_teacher(request)

    classes = get_teacher_classes(
        teacher
    )

    pupils = get_teacher_pupils(
        request
    )

    selected_pupil = None

    if pupil_id is not None:

        selected_pupil = get_object_or_404(
            Student.objects.select_related(
                "user",
                "class_room",
                "school",
            ),
            pk=pupil_id,
        )

        school = get_teacher_school(request)

        if (
            school is not None
            and selected_pupil.school_id != school.id
        ):
            return render(
                request,
                "errors/403.html",
                status=403,
            )

        if (
            selected_pupil.class_room_id
            and not teacher.assigned_class.filter(
                pk=selected_pupil.class_room_id
            ).exists()
        ):
            return render(
                request,
                "errors/403.html",
                status=403,
            )

    if request.method == "POST":

        post_pupil_id = request.POST.get(
            "pupil_id",
            pupil_id,
        )

        category = request.POST.get(
            "category",
            "positive",
        )

        note = request.POST.get(
            "note",
            "",
        ).strip()

        conduct_remark = request.POST.get(
            "conduct_remark",
            "",
        ).strip()

        is_report_card_remark = (
            request.POST.get(
                "is_report_card_remark"
            )
            in [
                "1",
                "true",
                "True",
                "on",
                "yes",
            ]
        )

        if not post_pupil_id:

            messages.error(
                request,
                "Please select a pupil.",
            )

        elif not note:

            messages.error(
                request,
                "Please enter a behavior note.",
            )

        else:

            pupil = get_object_or_404(
                Student.objects.select_related(
                    "school",
                    "class_room",
                ),
                pk=post_pupil_id,
            )

            school = get_teacher_school(request)

            if (
                school is not None
                and pupil.school_id != school.id
            ):
                return render(
                    request,
                    "errors/403.html",
                    status=403,
                )

            if (
                pupil.class_room_id
                and not teacher.assigned_class.filter(
                    pk=pupil.class_room_id
                ).exists()
            ):
                return render(
                    request,
                    "errors/403.html",
                    status=403,
                )

            BehaviorLog.objects.create(
                pupil=pupil,
                teacher=teacher,
                category=category,
                note=note,
                conduct_remark=conduct_remark,
                is_report_card_remark=is_report_card_remark,
            )

            messages.success(
                request,
                "Behavior record saved successfully.",
            )

            return redirect(
                "teacher_behavior"
            )

    behavior_logs = (
        BehaviorLog.objects
        .filter(
            teacher=teacher
        )
        .select_related(
            "pupil",
            "pupil__user",
        )
        .order_by(
            "-date"
        )
    )

    if selected_pupil:

        behavior_logs = behavior_logs.filter(
            pupil=selected_pupil
        )

    context = {
        "teacher": teacher,
        "classes": classes,

        "pupils": pupils,
        "students": pupils,

        "selected_pupil": selected_pupil,

        "behavior_logs": behavior_logs,

        "behavior_types": BehaviorLog.BEHAVIOR_TYPES,
    }

    return render(
        request,
        "teachersApp/behavior.html",
        context,
    )

# ============================================================
# CLASS PERFORMANCE
# ============================================================

@login_required
def teacher_class_performance(
    request,
    class_id,
):

    teacher = get_teacher(request)

    class_room = get_object_or_404(
        ClassRoom,
        pk=class_id,
    )

    if not teacher_has_access_to_class(
        teacher,
        class_room,
    ):
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    school = get_teacher_school(request)

    pupils = (
        Student.objects
        .filter(
            class_room=class_room
        )
        .select_related(
            "user",
            "class_room",
            "school",
        )
        .order_by(
            "user__first_name",
            "user__last_name",
        )
    )

    if school is not None:

        pupils = pupils.filter(
            school=school
        )

    records = (
        AcademicRecord.objects
        .filter(
            class_room=class_room
        )
        .select_related(
            "pupil",
            "pupil__user",
            "subject",
        )
        .order_by(
            "pupil__user__first_name",
            "pupil__user__last_name",
            "subject__subject",
        )
    )

    performance = []

    for pupil in pupils:

        pupil_records = records.filter(
            pupil=pupil
        )

        total_marks = 0
        total_max_marks = 0

        for record in pupil_records:

            if record.marks is not None:

                total_marks += float(
                    record.marks
                )

            if record.max_marks:

                total_max_marks += float(
                    record.max_marks
                )

        if total_max_marks > 0:

            percentage = round(
                (
                    total_marks
                    / total_max_marks
                )
                * 100,
                1,
            )

        else:

            percentage = 0

        if percentage >= 80:
            grade = "A"

        elif percentage >= 70:
            grade = "B"

        elif percentage >= 60:
            grade = "C"

        elif percentage >= 50:
            grade = "D"

        else:
            grade = "F"

        performance.append(
            {
                "pupil": pupil,
                "student": pupil,
                "records": pupil_records,
                "total_marks": total_marks,
                "total_max_marks": total_max_marks,
                "percentage": percentage,
                "grade": grade,
            }
        )

    context = {
        "teacher": teacher,
        "school": school,

        "class_room": class_room,
        "class": class_room,

        "pupils": pupils,
        "students": pupils,

        "records": records,
        "academic_records": records,

        "performance": performance,
    }

    return render(
        request,
        "teachersApp/class_performance.html",
        context,
    )


# ============================================================
# PRINT CLASS LIST
# ============================================================

@login_required
def teacher_print_class_list(
    request,
    class_id,
):

    teacher = get_teacher(request)

    class_room = get_object_or_404(
        ClassRoom,
        pk=class_id,
    )

    if not teacher_has_access_to_class(
        teacher,
        class_room,
    ):
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    school = get_teacher_school(request)

    pupils = (
        Student.objects
        .filter(
            class_room=class_room
        )
        .select_related(
            "user",
            "class_room",
            "school",
        )
        .order_by(
            "user__first_name",
            "user__last_name",
        )
    )

    if school is not None:

        pupils = pupils.filter(
            school=school
        )

    context = {
        "teacher": teacher,
        "school": school,

        "class_room": class_room,
        "class": class_room,

        "pupils": pupils,
        "students": pupils,
    }

    return render(
        request,
        "teachersApp/print_class_list.html",
        context,
    )


# ============================================================
# PRINT RESULTS
# ============================================================

@login_required
def teacher_print_results(
    request,
    class_id,
    subject_id,
):

    teacher = get_teacher(request)

    class_room = get_object_or_404(
        ClassRoom,
        pk=class_id,
    )

    subject = get_object_or_404(
        Subjects,
        pk=subject_id,
    )

    if not teacher_has_access_to_class(
        teacher,
        class_room,
    ):
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    if not teacher_has_access_to_subject(
        teacher,
        subject,
    ):
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    school = get_teacher_school(request)

    pupils = (
        Student.objects
        .filter(
            class_room=class_room
        )
        .select_related(
            "user",
            "class_room",
            "school",
        )
        .order_by(
            "user__first_name",
            "user__last_name",
        )
    )

    if school is not None:

        pupils = pupils.filter(
            school=school
        )

    records = (
        AcademicRecord.objects
        .filter(
            class_room=class_room,
            subject=subject,
        )
        .select_related(
            "pupil",
            "pupil__user",
            "subject",
        )
        .order_by(
            "pupil__user__first_name",
            "pupil__user__last_name",
        )
    )

    context = {
        "teacher": teacher,
        "school": school,

        "class_room": class_room,
        "class": class_room,

        "subject": subject,

        "pupils": pupils,
        "students": pupils,

        "records": records,
        "academic_records": records,
    }

    return render(
        request,
        "teachersApp/print_results.html",
        context,
    )


# ============================================================
# TEACHER RESOURCES
# ============================================================

@login_required
def teacher_resources(request):

    teacher = get_teacher(request)

    classes = get_teacher_classes(
        teacher
    )

    subjects = teacher.subject.all()

    context = {
        "teacher": teacher,
        "classes": classes,
        "subjects": subjects,
    }

    return render(
        request,
        "teachersApp/resources.html",
        context,
    )


# ============================================================
# FINAL TEST
# ============================================================

@login_required
def final_test(request):

    teacher = get_teacher(request)

    classes = get_teacher_classes(
        teacher
    )

    subjects = teacher.subject.all()

    context = {
        "teacher": teacher,
        "classes": classes,
        "subjects": subjects,
    }

    return render(
        request,
        "teachersApp/final_test.html",
        context,
    )
