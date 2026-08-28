from django.urls import path

from . import views


urlpatterns = [

    # ========================================================
    # TEACHER DASHBOARD
    # ========================================================

    path(
        "",
        views.dashboard_teacher,
        name="dashboard_teacher",
    ),

    path(
        "final/",
        views.dashboard_final,
        name="dashboard_final",
    ),

    # ========================================================
    # CLASSES
    # ========================================================

    path(
        "class/<int:class_id>/",
        views.teacher_class_detail,
        name="teacher_class_detail",
    ),

    # ========================================================
    # PUPIL REPORTS
    # ========================================================

    path(
        "report/<int:pupil_id>/",
        views.pupil_report_create_or_edit,
        name="pupil_report",
    ),

    # ========================================================
    # TIMETABLE
    # ========================================================

    path(
        "timetable/",
        views.teacher_timetable,
        name="teacher_timetable",
    ),

    # ========================================================
    # ASSIGNMENTS
    # ========================================================

    path(
        "assignments/",
        views.teacher_assignments,
        name="teacher_assignments",
    ),

    path(
        "assignments/create/",
        views.teacher_assignment_create,
        name="teacher_assignment_create",
    ),

    # ========================================================
    # ACADEMIC RECORDS
    # ========================================================

    path(
        "academic/",
        views.teacher_academic,
        name="teacher_academic",
    ),

    path(
        "academic/<int:class_id>/<int:subject_id>/",
        views.teacher_academic,
        name="teacher_academic_entry",
    ),

    # ========================================================
    # BEHAVIOR
    # ========================================================

    path(
        "behavior/",
        views.teacher_behavior,
        name="teacher_behavior",
    ),

    path(
        "behavior/<int:pupil_id>/",
        views.teacher_behavior,
        name="teacher_behavior_add",
    ),

    # ========================================================
    # PERFORMANCE
    # ========================================================

    path(
        "performance/<int:class_id>/",
        views.teacher_class_performance,
        name="teacher_class_performance",
    ),

    # ========================================================
    # PRINTING
    # ========================================================

    path(
        "print/class/<int:class_id>/",
        views.teacher_print_class_list,
        name="teacher_print_class_list",
    ),

    path(
        "print/results/<int:class_id>/<int:subject_id>/",
        views.teacher_print_results,
        name="teacher_print_results",
    ),

    # ========================================================
    # RESOURCES
    # ========================================================

    path(
        "resources/",
        views.teacher_resources,
        name="teacher_resources",
    ),

    # ========================================================
    # TEST
    # ========================================================

    path(
        "final_test/",
        views.final_test,
        name="final_test",
    ),
]