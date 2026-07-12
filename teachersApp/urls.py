from django.urls import path
from . import views

app_name = 'teachersApp'

urlpatterns = [
    # ---- Existing ----
    path('', views.dashboard_teacher, name='dashboard_teacher'),
    path('class/<int:class_id>/', views.teacher_class_detail, name='teacher_class_detail'),
    path('report/<int:pupil_id>/', views.pupil_report_create_or_edit, name='pupil_report'),

    # ---- Timetable ----
    path('timetable/', views.teacher_timetable, name='teacher_timetable'),

    # ---- Assignments ----
    path('assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('assignments/create/', views.teacher_assignment_create, name='teacher_assignment_create'),

    # ---- Academic (Marks) ----
    path('academic/', views.teacher_academic, name='teacher_academic'),
    path('academic/<int:class_id>/<int:subject_id>/', views.teacher_academic, name='teacher_academic_entry'),

    # ---- Behavior ----
    path('behavior/', views.teacher_behavior, name='teacher_behavior'),
    path('behavior/<int:pupil_id>/', views.teacher_behavior, name='teacher_behavior_add'),

    # ---- Class Performance ----
    path('performance/<int:class_id>/', views.teacher_class_performance, name='teacher_class_performance'),

    # ---- Print / Reports ----
    path('print/class/<int:class_id>/', views.teacher_print_class_list, name='teacher_print_class_list'),
    path('print/results/<int:class_id>/<int:subject_id>/', views.teacher_print_results, name='teacher_print_results'),
]