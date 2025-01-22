from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoom(models.Model):
    survey = models.ForeignKey('surveys.Survey', on_delete=models.CASCADE, related_name='chatrooms')
    users = models.ManyToManyField(User, related_name='chatrooms')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'ChatRoom for Survey {self.survey.id}'

class Message(models.Model):
    chatroom = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
