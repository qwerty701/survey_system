from django.urls import path
from .views import ChatMessagesView

urlpatterns = [
    path('<int:survey_id>/messages/', ChatMessagesView.as_view(), name='chat-messages'),
]