from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

from apps.surveys.models import Survey
from apps.notifications.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Survey)
def send_notification_on_survey_creation(sender, instance, created, **kwargs):
    if created:
        message = f'Создан новый опрос: {instance.title}'
        notification_type = 'survey_created'
        send_notification(instance.authors, message, notification_type)

@receiver(post_save, sender=Survey)
def send_notification_on_survey_end(sender, instance, **kwargs):
    if not instance.active and instance.time_end and now() > instance.time_end:
        message = f'Опрос "{instance.title}" завершен.'
        notification_type = 'survey_ended'
        send_notification(instance.authors, message, notification_type)

def send_notification(user, message, notification_type):
    Notification.objects.create(user=user, message=message, notification_type=notification_type)


    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user.id}',
        {
            'type': 'send_notification',
            'message': message,
            'notification_type': notification_type,
        }
    )