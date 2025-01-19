from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError, PermissionDenied
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from chats.models import ChatMessage

User = get_user_model()
logger = logging.getLogger(__name__)


class Category(models.Model):
    title  = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f'Категория {self.title}'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'



class Survey(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_survey')
    title = models.CharField(max_length=64)
    authors = models.ManyToManyField(User, related_name='authored_surveys')
    time_start = models.DateTimeField(auto_now_add=True)
    time_end = models.DateTimeField(verbose_name="Дата и время окончания вопроса")
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    def has_user_taken_survey(self, user):
        return UserResponse.objects.filter(user=user, survey=self).exists()

    @property
    def is_active(self):
        return now() < self.time_end

    def clean(self):
        if self.time_end <= now():
            raise ValidationError("Время окончания опроса должно быть в будущем.")
        if self.time_start and self.time_end <= self.time_start:
            raise ValidationError("Время окончания должно быть позже времени начала.")


    def save(self, *args, **kwargs):
        self.clean()
        if self.time_end and now() > self.time_end:
            self.active = False

        super().save(*args, **kwargs)

    def add_author(self, user):
        if user not in self.authors.all():
            self.authors.add(user)
        else:
            raise PermissionDenied("Этот пользователь уже является автором.")

    def __str__(self):
        return f'Опрос от {self.author}, название - {self.title}'

@receiver(post_save, sender=Survey)
def create_chat_for_survey(sender, instance, created, **kwargs):
    if created:
        ChatMessage.objects.create(
            survey=instance,
            user=instance.author,
            message="Чат для этого опроса создан!"
        )


@receiver(post_save, sender=Survey)
def create_chat_and_notify(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{instance.author.id}",
            {
                'type': 'notify_survey_creation',
                'survey_title': instance.title,
                'user_id': instance.author.id,
            }
        )

class Question(models.Model):
    TYPE_CHOICES = [
        ('text', 'Текстовый ответ'),
        ('choice', 'Выбор из вариантов'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='text')
    text = models.TextField()
    is_required = models.BooleanField(default=False, verbose_name='Обязательный вопрос')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f' вопрос - {self.text}'


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_options')
    text = models.CharField(max_length=255)
    votes = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_answer')

    def increment_votes(self):
        self.votes += 1
        self.save()

    def save(self, *args, **kwargs):
        if self.question.type != 'choice':
            raise ValidationError("Ответы могут быть созданы только для вопросов типа 'выбор из вариантов'.")
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.text}, Голоса - {self.votes}'

class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='user_responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_responses')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='user_responses', null=True, blank=True)
    text_response = models.TextField(null=True, blank=True)
    responsed_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if UserResponse.objects.filter(user=self.user, question=self.question).exists():
            raise ValidationError("Пользователь уже ответил на этот вопрос.")

        if self.question.type == 'text' and not self.text_response:
            raise ValidationError("Текстовый ответ обязателен для вопросов типа 'текстовый ответ'.")

        if self.question.type == 'choice' and not self.answer:
            raise ValidationError("Выбор ответа обязателен для вопросов типа 'выбор из вариантов'.")

        if self.answer and self.answer.question != self.question:
            raise ValidationError("Ответ не соответствует вопросу.")

        if UserResponse.objects.filter(user=self.user, survey=self.survey).exists():
            raise ValidationError("Вы уже проходили этот опрос.")

        if UserResponse.objects.filter(user=self.user, question=self.question).exists():
            raise ValidationError("Вы уже ответили на этот вопрос.")

        if self.survey.time_end and now() > self.survey.time_end:
            raise ValidationError("Опрос завершен, нельзя отправлять ответы.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} - {self.survey.title} - {self.question.text}'
