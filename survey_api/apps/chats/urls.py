from django.urls import path
from api.v1.chats.views import ChatMessagesView

urlpatterns = [
    path('<int:survey_id>/messages/', ChatMessagesView.as_view(), name='chat-messages'),
]