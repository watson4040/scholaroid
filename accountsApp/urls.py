from django.urls import path

from . import views


urlpatterns = [

    # ========================================================
    # HOME
    # ========================================================

    path(
        "",
        views.home,
        name="home",
    ),

    # ========================================================
    # PROFILE
    # ========================================================

    path(
        "profile/",
        views.profile_view,
        name="profile",
    ),

    # ========================================================
    # REGISTRATION
    # ========================================================

    path(
        "register/admin/",
        views.register_admin,
        name="register_admin",
    ),

    path(
        "register/teacher/",
        views.register_teacher,
        name="register_teacher",
    ),

    path(
        "register/pupil/",
        views.register_student,
        name="register_student",
    ),

    # Backward-compatible URL.
    # Internally the system still uses the old route name.
    path(
        "register/student/",
        views.register_student,
        name="register_student_legacy",
    ),

    path(
        "register/parent/",
        views.register_parent,
        name="register_parent",
    ),

    # ========================================================
    # AUTHENTICATION
    # ========================================================

    path(
        "login/",
        views.login_user,
        name="login",
    ),

    path(
        "logout/",
        views.logout_user,
        name="logout",
    ),

    path(
        "change-password/",
        views.change_password,
        name="change_password",
    ),

    # ========================================================
    # DASHBOARDS
    # ========================================================

    path(
        "dashboard/admin/",
        views.dashboard_admin,
        name="dashboard_admin",
    ),

    path(
        "dashboard/pupil/",
        views.dashboard_student,
        name="dashboard_student",
    ),

    path(
        "dashboard/parent/",
        views.dashboard_parent,
        name="dashboard_parent",
    ),

    # ========================================================
    # NOTICES
    # ========================================================

    path(
        "notices/",
        views.notice_list,
        name="notice_list",
    ),

    path(
        "notices/create/",
        views.notice_create,
        name="notice_create",
    ),
]