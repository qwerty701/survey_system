from django.db.models.signals import post_save
from django.dispatch import receiver
from surveys.models import Survey

@receiver(post_save, sender=Survey)
def create_chat_for_survey(sender, instance, created, **kwargs):
    if created:
        print(f"Чат для опроса {instance.title} создан.")