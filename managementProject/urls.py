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
    get_recent_messages,
    get_conversation_api,
    send_message_api,
    typing_indicator,
    delete_message,
    send_message_to_any,
)
# --- NEW IMPORT FOR TEACHER VIEWS ---
from teachersApp.views import teacher_class_detail, pupil_report_create_or_edit   # <--- ADD THIS

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
    # ---- NEW: class detail and report ----
    path('dashboard/teacher/class/<int:class_id>/', teacher_class_detail, name='teacher_class_detail'),
    path('dashboard/teacher/report/<int:pupil_id>/', pupil_report_create_or_edit, name='pupil_report'),   # <--- ADD THIS
    # ---- END NEW ----
    path('dashboard/student/', views.dashboard_student, name='dashboard_student'),
    path('dashboard/parent/', views.dashboard_parent, name='dashboard_parent'),
    path("notices/", views.notice_list, name="notice_list"),
    path("notices/create/", views.notice_create, name="notice_create"),
    path('change-password/', views.change_password, name='change_password'),
    path('enroll/', enrollment_request, name='enroll'),
    path('enroll/success/', enrollment_success, name='enrollment_success'),
    # Messaging URLs
    path('inbox/', user_inbox, name='inbox'),
    path('conversation/<int:user_id>/', conversation, name='conversation'),
    path('parent/message/', parent_send_message, name='parent_send_message'),
    path('admin-inbox/', admin_message_list, name='admin_message_list'),
    path('admin/message/<int:pk>/', admin_message_detail, name='admin_message_detail'),
    path('send/', send_message_to_any, name='send_message_to_any'),
    # API endpoints
    path('api/recent-messages/', get_recent_messages, name='get_recent_messages'),
    path('api/conversation/<int:user_id>/', get_conversation_api, name='get_conversation_api'),
    path('api/send-message/<int:user_id>/', send_message_api, name='send_message_api'),
    path('api/typing/', typing_indicator, name='typing_indicator'),
    path('api/delete-message/', delete_message, name='delete_message'),
    # Exams app
    path('exams/', include('examsApp.urls')),
    path('fees/', include('feesApp.urls')),
]