from django.urls import path
from . import views

app_name = 'teachersApp'

urlpatterns = [
    path('', views.dashboard_teacher, name='dashboard_teacher'),
    path('class/<int:class_id>/', views.teacher_class_detail, name='teacher_class_detail'),
    path('report/<int:pupil_id>/', views.pupil_report_create_or_edit, name='pupil_report'),
]