from django.urls import path

from api.v1.chats.views import get_message_history

urlpatterns = [
    path("<int:room_id>/messages/", get_message_history, name="chat-messages"),
]
