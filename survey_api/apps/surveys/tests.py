import os

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils.timezone import now, timedelta
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from .models import Answer, Category, Question, Survey

User = get_user_model()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "survey_api.settings")


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.BasicAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.IsAuthenticated",
        ],
    }
)
class SurveyTests(TestCase):
    def setUp(self):

        self.user1 = User.objects.create_user(username="user1", password="password1")
        self.user2 = User.objects.create_user(username="user2", password="password2")
        self.category = Category.objects.create(title="Test Category")

        self.survey = Survey.objects.create(
            category=self.category,
            title="Test Survey",
            authors=self.user1,
            time_end=now() + timedelta(days=1),
            description="Test Description",
        )

        self.text_question = Question.objects.create(
            survey=self.survey, text="What is your name?", type="text", order=1
        )

        self.choice_question = Question.objects.create(
            survey=self.survey,
            text="What is your favorite color?",
            type="choice",
            order=2,
        )

        self.answer1 = Answer.objects.create(question=self.choice_question, text="Red")
        self.answer2 = Answer.objects.create(question=self.choice_question, text="Blue")

        self.client = APIClient()

    def test_survey_creation(self):
        """Тест на создание опроса."""
        self.assertEqual(Survey.objects.count(), 1)
        self.assertEqual(self.survey.title, "Test Survey")
        self.assertTrue(self.survey.is_active)

    def test_survey_time_validation(self):
        """Тест валидации времени окончания опроса."""
        with self.assertRaises(Exception):
            Survey.objects.create(
                category=self.category,
                title="Invalid Survey",
                authors=self.user1,
                time_end=now() - timedelta(days=1),
            )

    def test_add_response_text_question(self):
        question = Question.objects.create(
            text="Text question?",
            survey=self.survey,
            type="text",
            is_required=True,
        )

        response = self.client.post(
            f"api/v1/surveys/{self.survey.id}/submit-response/",
            {"question": question.id, "text_response": "This is an answer"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_response_choice_question(self):
        question = Question.objects.create(
            text="Choice question?",
            survey=self.survey,
            type="choice",
            is_required=True,
        )
        answer = Answer.objects.create(question=question, text="Option 1")

        response = self.client.post(
            f"/api/v1/surveys/{self.survey.id}/submit-response/",
            {"question": question.id, "answer": answer.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_double_response_not_allowed(self):
        question = Question.objects.create(
            text="Double response question?",
            survey=self.survey,
            type="choice",
            is_required=True,
        )
        answer = Answer.objects.create(question=question, text="Option 1")

        self.client.post(
            f"api/v1/surveys/{self.survey.id}/submit-response/",
            {"question": question.id, "answer": answer.id},
            format="json",
        )

        response = self.client.post(
            f"api/v1/surveys/{self.survey.id}/submit-response/",
            {"question": question.id, "answer": answer.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_export_responses_csv(self):
        """Тест экспорта ответов в формате CSV."""
        self.client.force_authenticate(user=self.user2)

        self.client.post(
            f"/surveys/{self.survey.id}/submit-response/",
            {
                "question": self.choice_question.id,
                "answer": self.answer1.id,
            },
        )

        response = self.client.get(
            f"/surveys/{self.survey.id}/export-responses/?format=csv"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("attachment; filename=", response.headers["Content-Disposition"])

    def test_survey_deactivation(self):

        self.survey.time_end = now() + timedelta(hours=1)
        self.survey.save()
        self.assertTrue(self.survey.is_active)

        self.survey.time_end = now() - timedelta(hours=1)
        self.survey.save()
        self.assertFalse(self.survey.is_active)

    def test_increment_votes(self):
        self.answer1.increment_votes(self.user2)
        self.answer1.refresh_from_db()
        self.assertEqual(self.answer1.votes, 1)

        with self.assertRaises(ValidationError):
            self.answer1.increment_votes(self.user2)
