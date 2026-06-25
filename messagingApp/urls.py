from django.urls import path
from . import views

urlpatterns = [
    # Main inbox (grouped conversations)
    path('inbox/', views.user_inbox, name='inbox'),
    
    # Conversation with a specific user
    path('conversation/<int:user_id>/', views.conversation, name='conversation'),
    
    # Parent sends a new message (creates conversation with admin)
    path('parent/message/', views.parent_send_message, name='parent_send_message'),
    
    # Admin views
    path('admin/messages/', views.admin_message_list, name='admin_message_list'),
    path('admin/message/<int:pk>/', views.admin_message_detail, name='admin_message_detail'),
    
    # Group chat features (keep if needed)
    path("groups/", views.groups, name="groups"),
    path("groups/create/", views.create_group, name="create_group"),
    path("groups/<int:group_id>/", views.group_chat, name="group_chat"),
    
    # Polling / real-time (if you have WebSocket)
    path("conversation/<int:user_id>/poll/", views.conversation_poll, name="conversation_poll"),
    path("groups/<int:group_id>/poll/", views.group_poll, name="group_poll"),
    
    # Search and reactions
    path("search/", views.search_messages, name="search_messages"),
    path("react/", views.react, name="react_message"),
    
    # File uploads
    path('upload/direct/<int:user_id>/', views.upload_direct, name='upload_direct'),
    path('upload/group/<int:group_id>/', views.upload_group, name='upload_group'),
]