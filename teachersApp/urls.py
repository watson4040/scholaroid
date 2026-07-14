from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_teacher, name='dashboard_teacher'),
    path('class/<int:class_id>/', views.teacher_class_detail, name='teacher_class_detail'),
    path('report/<int:pupil_id>/', views.pupil_report_create_or_edit, name='pupil_report'),
    path('timetable/', views.teacher_timetable, name='teacher_timetable'),
    path('assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('assignments/create/', views.teacher_assignment_create, name='teacher_assignment_create'),
    path('academic/', views.teacher_academic, name='teacher_academic'),
    path('academic/<int:class_id>/<int:subject_id>/', views.teacher_academic, name='teacher_academic_entry'),
    path('behavior/', views.teacher_behavior, name='teacher_behavior'),
    path('behavior/<int:pupil_id>/', views.teacher_behavior, name='teacher_behavior_add'),
    path('performance/<int:class_id>/', views.teacher_class_performance, name='teacher_class_performance'),
    path('print/class/<int:class_id>/', views.teacher_print_class_list, name='teacher_print_class_list'),
    path('print/results/<int:class_id>/<int:subject_id>/', views.teacher_print_results, name='teacher_print_results'),
    path('resources/', views.teacher_resources, name='teacher_resources'),
    path('test/', views.dashboard_new_test, name='dashboard_new_test'),   # <-- test URL
]