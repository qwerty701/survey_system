from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.surveys.models import ChatRoom, Message, Survey

User = get_user_model()


@receiver(post_save, sender=Survey)
def create_chat_for_survey(sender, instance, created, **kwargs):
    if created:
        chatroom = ChatRoom.objects.create(survey=instance)

        chatroom.users.add(instance.authors)

        Message.objects.create(
            chatroom=chatroom, sender=instance.authors, content="Начало чата"
        )
