import pandas as pd
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.surveys.models import Answer, Category, Question, Survey, UserResponse
from apps.surveys.permissions import IsAuthorOrAdmin
from apps.surveys.serializers import (
    AnswerSerializer,
    CategorySerializer,
    QuestionSerializer,
    SurveySerializer,
    UserResponseSerializer,
)
from apps.users.permissions import IsOwner


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwner(), IsAuthorOrAdmin()]
        else:
            return [AllowAny()]


class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "authors", "active"]
    search_fields = ["title"]

    def perform_create(self, serializer):
        serializer.save(authors=self.request.user)

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAuthorOrAdmin()]
        else:
            return [AllowAny()]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy", "create"]:
            return [IsAuthenticated(), IsAuthorOrAdmin()]
        else:
            return [AllowAny()]


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer


class SubmitResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        survey_id = kwargs.get("survey_id")
        data = request.data

        try:
            question = Question.objects.get(
                id=data.get("question"), survey_id=survey_id
            )
        except Question.DoesNotExist:
            return Response(
                {"error": "Вопрос не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        if question.type == "choice":
            answer_id = data.get("answer")
            try:
                answer = Answer.objects.get(id=answer_id, question=question)
            except Answer.DoesNotExist:
                return Response(
                    {"error": "Ответ не найден"}, status=status.HTTP_404_NOT_FOUND
                )
            try:
                answer.increment_votes(user)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            response, created = UserResponse.objects.get_or_create(
                user=user, survey_id=survey_id, question=question, answer=answer
            )

            if not created:
                return Response(
                    {"error": "Вы уже ответили на этот вопрос."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"message": "Ответ сохранен успешно"}, status=status.HTTP_200_OK
            )

        elif question.type == "text":
            text_response = data.get("text_response")
            if not text_response:
                return Response(
                    {"error": "Необходимо указать текстовый ответ"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response, created = UserResponse.objects.get_or_create(
                user=user,
                survey_id=survey_id,
                question=question,
                defaults={"text_response": text_response},
            )

            if not created:
                return Response(
                    {"error": "Вы уже ответили на этот вопрос."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"message": "Текстовый ответ сохранен успешно"},
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {"error": "Неподдерживаемый тип вопроса"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ExportResponsesView(APIView):
    permission_classes = [IsAuthorOrAdmin]

    def get_object(self, survey_id):
        try:
            return Survey.objects.get(id=survey_id)
        except Survey.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        survey_id = kwargs.get("survey_id")
        survey = self.get_object(survey_id)

        if not survey:
            return Response({"error": "Опрос не найден"}, status=404)

        if not IsAuthorOrAdmin().has_object_permission(request, self, survey):
            return Response(
                {"error": "У вас нет прав на экспорт результатов этого опроса"},
                status=403,
            )

        format = request.query_params.get("format", "csv")

        responses = UserResponse.objects.filter(survey_id=survey_id).values(
            "user__username",
            "survey__title",
            "question__text",
            "answer__text",
            "text_response",
            "responsed_at",
        )

        for response in responses:
            if "responsed_at" in response and response["responsed_at"]:
                response["responsed_at"] = response["responsed_at"].replace(tzinfo=None)

        df = pd.DataFrame(responses)

        if format == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="survey_{survey_id}_responses.csv"'
            )
            df.to_csv(path_or_buf=response, index=False)
            return response

        elif format == "xlsx":
            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="survey_{survey_id}_responses.xlsx"'
            )
            with pd.ExcelWriter(response, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            return response

        else:
            return Response({"error": "Неподдерживаемый формат"}, status=400)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ProtectedView(APIView):
    def get(self, request):
        return Response({"message": "Это защищенный endpoint!"})


class UserResponseViewSet(viewsets.ModelViewSet):
    queryset = UserResponse.objects.all()
    serializer_class = UserResponseSerializer
