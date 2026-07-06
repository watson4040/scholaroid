from django.urls import path
from . import views

app_name = 'teachersApp'

urlpatterns = [
    path('', views.dashboard_teacher, name='dashboard_teacher'),
    path('class/<int:class_id>/', views.teacher_class_detail, name='teacher_class_detail'),
    # Add other URLs if you have them, e.g.:
    # path('exams/', views.teacher_exams_list, name='teacher_exams_list'),
    # path('notices/', views.notice_list, name='notice_list'),
    # path('resources/', views.teacher_resources, name='teacher_resources'),
    # path('inbox/', views.inbox, name='inbox'),
]