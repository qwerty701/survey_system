from rest_framework import serializers

from .models import Answer, Category, Question, Survey, UserResponse


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text", "votes"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["id", "text", "type", "is_required", "answers"]

    def get_answers(self, obj):
        if obj.type == "choice":
            answers = Answer.objects.filter(question=obj)
            return AnswerSerializer(answers, many=True).data
        return None


class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = [
            "id",
            "category",
            "title",
            "authors",
            "time_end",
            "active",
            "description",
            "questions",
        ]


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = [
            "id",
            "user",
            "survey",
            "question",
            "answer",
            "text_response",
            "responsed_at",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title"]
