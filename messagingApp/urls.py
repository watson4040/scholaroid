from django.urls import path
from . import views

urlpatterns = [
    # Main inbox (grouped conversations)
    path('inbox/', views.user_inbox, name='inbox'),
    
    # Conversation with a specific user (HTML view)
    path('conversation/<int:user_id>/', views.conversation, name='conversation'),
    
    # Parent sends a new message (creates conversation with admin)
    path('parent/message/', views.parent_send_message, name='parent_send_message'),
    
    # Admin views
    path('admin/messages/', views.admin_message_list, name='admin_message_list'),
    path('admin/message/<int:pk>/', views.admin_message_detail, name='admin_message_detail'),
    
    # ---- API endpoints (for AJAX) ----
    path('api/recent-messages/', views.get_recent_messages, name='get_recent_messages'),
    path('api/conversation/<int:user_id>/', views.get_conversation_api, name='get_conversation_api'),
    path('api/send-message/<int:user_id>/', views.send_message_api, name='send_message_api'),
    path('api/typing/', views.typing_indicator, name='typing_indicator'),
    path('api/delete-message/', views.delete_message, name='delete_message'),
    path('api/clear-conversation/<int:user_id>/', views.clear_conversation_api, name='clear_conversation_api'),
]