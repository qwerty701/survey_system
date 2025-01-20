from rest_framework import serializers
from .models import Answer, Survey, Question, UserResponse, Category


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['id', 'category', 'title', 'authors', 'time_end', 'active', 'description']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'type', 'is_required', 'survey', 'order']


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = ['id', 'user', 'survey', 'question', 'answer', 'text_response', 'responsed_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'text', 'votes', 'user_voted']