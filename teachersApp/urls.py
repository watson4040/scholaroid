from django.urls import path
from . import views

app_name = 'teachersApp'

urlpatterns = [
    # Teacher dashboard
    path('', views.dashboard_teacher, name='dashboard_teacher'),
    # Class attendance page – IMPORTANT: name must be 'teacher_class_detail'
    path('class/<int:class_id>/', views.teacher_class_detail, name='teacher_class_detail'),
    # Add other routes if needed (e.g., report, etc.)
]