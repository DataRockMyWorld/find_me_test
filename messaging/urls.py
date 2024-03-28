# messaging/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListView.as_view(), name='conversation_list'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('conversations/<int:conv_id>/send_message/', views.SendMessageView.as_view(), name='send_message'),
    path('message_user/<int:user_id>/', views.message_user, name='message_user'),
]
