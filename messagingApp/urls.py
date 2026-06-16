from django.urls import path
from . import views
from .views import (
    inbox, conversation, group_chat, search_messages, react,
    conversation_poll, group_poll, upload_direct, upload_group
)
from messagingApp.views import parent_send_message, admin_message_list, admin_message_detail

urlpatterns = [

# ... inside urlpatterns:
    path('parent/message/', parent_send_message, name='parent_send_message'),
    path('admin/messages/', admin_message_list, name='admin_message_list'),
    path('admin/message/<int:pk>/', admin_message_detail, name='admin_message_detail'),
    path("inbox/", views.inbox, name="inbox"),
    path("conversation/<int:user_id>/", views.conversation, name="conversation"),
    path("groups/", views.groups, name="groups"),
    path("groups/create/", views.create_group, name="create_group"),
    path("groups/<int:group_id>/", views.group_chat, name="group_chat"),
    path("conversation/<int:user_id>/poll/", views.conversation_poll, name="conversation_poll"),
    path("groups/<int:group_id>/poll/", views.group_poll, name="group_poll"),
    path("search/", views.search_messages, name="search_messages"),
    path("react/", views.react, name="react_message"),
        path('upload/direct/<int:user_id>/', views.upload_direct, name='upload_direct'),
        path('upload/group/<int:group_id>/', views.upload_group, name='upload_group'),
        
]