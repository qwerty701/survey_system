from rest_framework import serializers
from .models import Answer, Survey, Question, UserResponse, Category


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['category', 'title', 'authors', 'time_end', 'active', 'description']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['text', 'type', 'is_required', 'survey', 'order']


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = ['user', 'survey', 'question', 'answer', 'text_response', 'responsed_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'votes', 'user']