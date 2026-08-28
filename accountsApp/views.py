
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q

from .forms import (
    AdminRegistrationForm,
    TeacherRegistrationForm,
    StudentRegistrationForm,
    ParentRegistrationForm,
    ProfileForm,
    NoticeForm,
    ChangePasswordForm,
)

from .models import Notice

from studentsApp.models import Student
from teachersApp.models import Teacher, AcademicRecord
from classesApp.models import ClassRoom
from attendanceApp.models import Attendance
from examsApp.models import Exam
from messagingApp.models import Message
from parentsApp.models import Parent


User = get_user_model()


# ============================================================
# HOME
# ============================================================

def home(request):
    return render(request, "home.html")


# ============================================================
# REGISTRATION
# ============================================================

def register_admin(request):
    if request.method == "POST":
        form = AdminRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "redirect_url": reverse("home"),
                    }
                )

            return redirect("home")

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "field_errors": {
                        field: list(errors)
                        for field, errors in form.errors.items()
                    },
                },
                status=400,
            )

    else:
        form = AdminRegistrationForm()

    return render(
        request,
        "accountsApp/register.html",
        {"form": form},
    )


def register_teacher(request):
    if request.method == "POST":
        form = TeacherRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "redirect_url": reverse("home"),
                    }
                )

            return redirect("home")

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "field_errors": {
                        field: list(errors)
                        for field, errors in form.errors.items()
                    },
                },
                status=400,
            )

    else:
        form = TeacherRegistrationForm()

    return render(
        request,
        "accountsApp/register.html",
        {"form": form},
    )


def register_student(request):
    """
    Registration endpoint retained as register_student for
    compatibility with the existing URL configuration.

    User-facing terminology remains Pupil/Pupils.
    """

    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "redirect_url": reverse("home"),
                    }
                )

            return redirect("home")

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "field_errors": {
                        field: list(errors)
                        for field, errors in form.errors.items()
                    },
                },
                status=400,
            )

    else:
        form = StudentRegistrationForm()

    return render(
        request,
        "accountsApp/register.html",
        {"form": form},
    )


def register_parent(request):
    if request.method == "POST":
        form = ParentRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )

            try:
                parent_profile = Parent.objects.get(user=user)

                matches = Student.objects.filter(
                    parent__isnull=True,
                    parent_email__iexact=user.email,
                )

                for pupil in matches:
                    pupil.parent = parent_profile
                    pupil.save(update_fields=["parent"])

                if matches.exists():
                    messages.success(
                        request,
                        f"Linked {matches.count()} pupil(s) to your parent account.",
                    )

            except Parent.DoesNotExist:
                pass

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "redirect_url": reverse("home"),
                    }
                )

            return redirect("home")

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "field_errors": {
                        field: list(errors)
                        for field, errors in form.errors.items()
                    },
                },
                status=400,
            )

    else:
        form = ParentRegistrationForm()

    return render(
        request,
        "accountsApp/register.html",
        {"form": form},
    )


# ============================================================
# LOGIN
# ============================================================

def login_user(request):
    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(request, user)

            role = getattr(user, "role", None)

            # ------------------------------------------------
            # ADMIN
            # ------------------------------------------------

            if (
                user.is_superuser
                or user.is_staff
                or role == "admin"
            ):
                redirect_name = "dashboard_admin"

            # ------------------------------------------------
            # TEACHER
            # ------------------------------------------------

            elif role == "teacher":
                redirect_name = "dashboard_teacher"

            # ------------------------------------------------
            # PUPIL
            # ------------------------------------------------

            elif role == "pupil":
                redirect_name = "dashboard_student"

            # ------------------------------------------------
            # PARENT
            # ------------------------------------------------

            elif role == "parent":
                redirect_name = "dashboard_parent"

            else:
                redirect_name = "home"

            try:
                redirect_url = reverse(redirect_name)
            except Exception:
                redirect_url = reverse("home")

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "redirect_url": redirect_url,
                    }
                )

            return redirect(redirect_url)

        # ----------------------------------------------------
        # INVALID LOGIN
        # ----------------------------------------------------

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "errors": [
                        "Invalid credentials. Please try again."
                    ],
                },
                status=400,
            )

        messages.error(
            request,
            "Invalid credentials. Please try again.",
        )

    return render(
        request,
        "accountsApp/login.html",
    )


# ============================================================
# LOGOUT
# ============================================================

@login_required
def logout_user(request):
    logout(request)
    return redirect("home")


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@login_required
def dashboard_admin(request):

    if not (
        request.user.is_superuser
        or request.user.is_staff
        or getattr(request.user, "role", None) == "admin"
    ):
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    context = {
        "student_count": Student.objects.count(),
        "teacher_count": Teacher.objects.count(),
        "parent_count": Parent.objects.count(),
        "class_count": ClassRoom.objects.count(),
        "exam_count": Exam.objects.count(),
        "notification_count": Notice.objects.count(),

        "recent_attendance": Attendance.objects.order_by(
            "-date"
        )[:5],

        "recent_messages": Message.objects.order_by(
            "-timestamp"
        )[:5],

        "recent_exams": Exam.objects.order_by(
            "-exam_date"
        )[:5],

        "recent_students": Student.objects.order_by(
            "-admission_date"
        )[:5],

        "recent_notifications": Notice.objects.order_by(
            "-created_at"
        )[:5],

        "active_users": User.objects.filter(
            is_active=True
        ).count(),
    }

    return render(
        request,
        "accountsApp/dashboard.html",
        context,
    )


# ============================================================
# PUPIL DASHBOARD
# ============================================================

@login_required
def dashboard_student(request):
    """
    Pupil dashboard.

    The internal Django model remains Student for compatibility.
    The user-facing terminology is Pupil/Pupils.
    """

    pupil = get_object_or_404(
        Student.objects.select_related(
            "user",
            "class_room",
        ),
        user=request.user,
    )

    # --------------------------------------------------------
    # ATTENDANCE
    # --------------------------------------------------------

    attendance_records = (
        Attendance.objects
        .filter(student=pupil)
        .order_by("-date")
    )

    total_attendance = attendance_records.count()

    present_count = attendance_records.filter(
        status="present"
    ).count()

    attendance_percentage = (
        round((present_count / total_attendance) * 100)
        if total_attendance
        else 0
    )

    # --------------------------------------------------------
    # EXAMS
    # --------------------------------------------------------

    if pupil.class_room_id:
        exams = (
            Exam.objects
            .filter(class_room=pupil.class_room)
            .select_related(
                "subject",
                "class_room",
            )
            .order_by("exam_date")
        )
    else:
        exams = Exam.objects.none()

    # --------------------------------------------------------
    # ACADEMIC RECORDS
    # --------------------------------------------------------

    records = (
        AcademicRecord.objects
        .filter(pupil=pupil)
        .select_related(
            "subject",
            "class_room",
        )
        .order_by("-date_recorded")[:20]
    )

    student_results = []

    for record in records:

        marks = (
            float(record.marks)
            if record.marks is not None
            else 0
        )

        maximum = (
            float(record.max_marks)
            if record.max_marks
            else 0
        )

        percentage = (
            round((marks / maximum) * 100, 1)
            if maximum > 0
            else 0
        )

        # ----------------------------------------------------
        # GRADE
        # ----------------------------------------------------

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

        student_results.append(
            {
                "subject": record.subject,
                "term": record.get_term_display(),
                "exam_type": record.get_exam_type_display(),
                "marks": record.marks,
                "max_marks": record.max_marks,
                "percentage": percentage,
                "grade": grade,
                "date_recorded": record.date_recorded,
            }
        )

    # --------------------------------------------------------
    # NOTICES
    # --------------------------------------------------------

    notices = Notice.objects.order_by(
        "-created_at"
    )[:8]

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {
        "student": pupil,
        "pupil": pupil,

        "attendance_records": attendance_records[:10],

        "attendance_percentage": attendance_percentage,

        "exams": exams[:6],

        "notices": notices,

        "student_results": student_results,

        "stats": {
            "upcoming_exams": exams.count(),
            "attendance_pct": attendance_percentage,
            "notices": notices.count(),
        },
    }

    return render(
        request,
        "accountsApp/dashboard_student.html",
        context,
    )


# ============================================================
# TEACHER DASHBOARD
# ============================================================

@login_required
def dashboard_teacher(request):
    """
    Teacher dashboard entry point.

    The actual dashboard is rendered by the teachersApp view.
    This function keeps the global URL name dashboard_teacher
    stable for login redirects.
    """

    return redirect("dashboard_final")


# ============================================================
# PARENT DASHBOARD
# ============================================================

@login_required
def dashboard_parent(request):

    parent = get_object_or_404(
        Parent,
        user=request.user,
    )

    children = (
        Student.objects
        .filter(parent=parent)
        .select_related(
            "user",
            "class_room",
        )
    )

    children_data = []

    for child in children:

        attendance = (
            Attendance.objects
            .filter(student=child)
            .order_by("-date")[:5]
        )

        if child.class_room_id:

            exams = (
                Exam.objects
                .filter(class_room=child.class_room)
                .select_related("subject")
                .order_by("exam_date")[:3]
            )

        else:

            exams = Exam.objects.none()

        children_data.append(
            {
                "student": child,
                "pupil": child,
                "attendance": attendance,
                "exams": exams,
            }
        )

    notices = Notice.objects.order_by(
        "-created_at"
    )[:5]

    recent_messages = (
        Message.objects
        .filter(
            Q(sender=parent.user)
            | Q(recipient=parent.user)
        )
        .order_by("-timestamp")[:5]
    )

    context = {
        "parent": parent,
        "children": children,
        "children_data": children_data,
        "notices": notices,
        "recent_messages": recent_messages,
    }

    return render(
        request,
        "accountsApp/dashboard_parent.html",
        context,
    )


# ============================================================
# PROFILE
# ============================================================

@login_required
def profile_view(request):

    if request.method == "POST":

        # ----------------------------------------------------
        # REMOVE PROFILE PHOTO
        # ----------------------------------------------------

        if "remove_photo" in request.POST:

            if request.user.profile_photo:
                request.user.profile_photo.delete(
                    save=False
                )

            request.user.profile_photo = None

            request.user.save(
                update_fields=["profile_photo"]
            )

            messages.success(
                request,
                "Profile photo removed.",
            )

            return redirect("profile")

        # ----------------------------------------------------
        # UPDATE PROFILE
        # ----------------------------------------------------

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully.",
            )

            return redirect("profile")

        messages.error(
            request,
            "Please fix the errors below.",
        )

    else:

        form = ProfileForm(
            instance=request.user
        )

    return render(
        request,
        "accountsApp/profile.html",
        {
            "form": form
        },
    )


# ============================================================
# NOTICES
# ============================================================

@login_required
def notice_list(request):

    notices = Notice.objects.order_by(
        "-created_at"
    )

    return render(
        request,
        "accountsApp/notice_list.html",
        {
            "notices": notices
        },
    )


@login_required
def notice_create(request):

    if not (
        request.user.is_superuser
        or request.user.is_staff
        or getattr(request.user, "role", None) == "admin"
    ):
        return redirect("notice_list")

    if request.method == "POST":

        form = NoticeForm(request.POST)

        if form.is_valid():

            notice = form.save(
                commit=False
            )

            notice.created_by = request.user

            notice.save()

            messages.success(
                request,
                "Notice created successfully.",
            )

            return redirect(
                "notice_list"
            )

    else:

        form = NoticeForm()

    return render(
        request,
        "accountsApp/notice_form.html",
        {
            "form": form
        },
    )


# ============================================================
# CHANGE PASSWORD
# ============================================================

@login_required
def change_password(request):

    if request.method == "POST":

        form = ChangePasswordForm(
            request.user,
            request.POST,
        )

        if form.is_valid():

            new_password = form.cleaned_data[
                "new_password1"
            ]

            request.user.set_password(
                new_password
            )

            request.user.save(
                update_fields=["password"]
            )

            update_session_auth_hash(
                request,
                request.user,
            )

            messages.success(
                request,
                "Your password has been changed successfully.",
            )

            return redirect(
                "profile"
            )

    else:

        form = ChangePasswordForm(
            request.user
        )

    return render(
        request,
        "accountsApp/change_password.html",
        {
            "form": form
        },
    )