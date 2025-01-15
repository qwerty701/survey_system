from django.db import models
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError
from users.models import User


class Category(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return f'Категория {self.title}'

class Survey(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_survey')
    title = models.CharField(max_length=64)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    time_end = models.DateTimeField()
    active = models.BooleanField(default=True)

    def clean(self):
        def clean(self):
            if self.end_time <= now():
                raise ValidationError("End time must be in the future.")

    def save(self, *args, **kwargs):
        self.clean()
        if self.time_end and now() > self.time_end:
            self.active = False

        super().save(*args, **kwargs)

        if not self.author.surveys_create.filter(id=self.id).exists():
            self.author.surveys_create.add(self)

    def __str__(self):
        return f'Опрос от {self.author}, название - {self.title}'

class Question(models.Model):
    TYPES = [
        ('text', 'Текстовый ответ'),
        ('choice', 'Выбор из вариантов'),
    ]
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='question_survey')
    text = models.TextField()
    type = models.CharField(max_length=7, choices=TYPES, default=text)

    def __str__(self):
        return f' вопрос - {self.text}'


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_options')
    text = models.CharField(max_length=255)
    votes = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_answer')

    def __str__(self):
        return f'{self.text}, Голоса - {self.votes}'

class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='user_responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_responses')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='user_responses', null=True, blank=True)
    text_response = models.TextField(null=True, blank=True)
    responsed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.survey.title} - {self.question.text}'
