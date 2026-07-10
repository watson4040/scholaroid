from django.urls import path
from . import views

app_name = 'teachersApp'

urlpatterns = [
    # Teacher dashboard
    path('', views.dashboard_teacher, name='dashboard_teacher'),
    # Class attendance page
    path('class/<int:class_id>/', views.teacher_class_detail, name='teacher_class_detail'),
    # Pupil report (teacher comment)
    path('report/<int:pupil_id>/', views.pupil_report_create_or_edit, name='pupil_report'),
    # Optional: report with explicit term and year
    path('report/<int:pupil_id>/<str:term>/<str:year>/', views.pupil_report_create_or_edit, name='pupil_report_with_term'),
]