from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_teacher, name='dashboard_teacher'),
    path('class/<int:class_id>/', views.teacher_class_detail, name='teacher_class_detail'),
    # Add any other URLs you already have (like admin lists, etc.)
]