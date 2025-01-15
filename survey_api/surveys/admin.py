from django.contrib import admin
from .models import Survey, Question, Answer, Category

admin.site.register(Category)
admin.site.register(Answer)
admin.site.register(Question)
admin.site.register(Survey)
