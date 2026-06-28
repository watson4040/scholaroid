from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.user_inbox, name='inbox'),
    path('conversation/<int:user_id>/', views.conversation, name='conversation'),
    path('parent/message/', views.parent_send_message, name='parent_send_message'),
    path('admin/messages/', views.admin_message_list, name='admin_message_list'),
    path('admin/message/<int:pk>/', views.admin_message_detail, name='admin_message_detail'),
    path('api/recent-messages/', views.get_recent_messages, name='get_recent_messages'),
    path('api/typing/', views.typing_indicator, name='typing_indicator'),
    path('api/delete-message/', views.delete_message, name='delete_message'),
]