from django.urls import path, include
from django.contrib import admin
from . import views
from studentsApp.views import enrollment_request, enrollment_success
from messagingApp.views import (
    parent_send_message,
    admin_message_list,
    admin_message_detail,
    user_inbox,
    conversation,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('register/admin/', views.register_admin, name='register_admin'),
    path('register/teacher/', views.register_teacher, name='register_teacher'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/parent/', views.register_parent, name='register_parent'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/teacher/', views.dashboard_teacher, name='dashboard_teacher'),
    path('dashboard/student/', views.dashboard_student, name='dashboard_student'),
    path('dashboard/parent/', views.dashboard_parent, name='dashboard_parent'),
    path("notices/", views.notice_list, name="notice_list"),
    path("notices/create/", views.notice_create, name="notice_create"),
    path('change-password/', views.change_password, name='change_password'),
    path('enroll/', enrollment_request, name='enroll'),
    path('enroll/success/', enrollment_success, name='enrollment_success'),

    # Messaging URLs – changed to match hardcoded link
    path('inbox/', user_inbox, name='inbox'),
    path('conversation/<int:user_id>/', conversation, name='conversation'),
    path('parent/message/', parent_send_message, name='parent_send_message'),
    path('admin-inbox/', admin_message_list, name='admin_message_list'),   # <-- changed from /admin/messages/
    path('admin/message/<int:pk>/', admin_message_detail, name='admin_message_detail'),

    path('fees/', include('feesApp.urls')),
]