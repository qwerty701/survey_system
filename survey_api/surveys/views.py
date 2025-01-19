from django.utils.timezone import now
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, filters, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import *
from .utils import has_user_completed_survey

from .models import Survey, Question, Answer, UserResponse

import pandas as pd
from django.http import HttpResponse


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'authors', 'active']
    search_fields = ['title']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer


class SubmitResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserResponseSerializer(data=request.data)
        if serializer.is_valid():
            survey = serializer.validated_data['survey']
            if not survey.active:
                return Response(
                    {"error": "Опрос не активен."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if survey.time_end and now() > survey.time_end:
                return Response(
                    {"error": "Опрос завершен."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                user_response = serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": f"Ошибка сохранения ответа: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExportResponsesView(APIView):
    def get(self, request, *args, **kwargs):
        format = request.query_params.get('format', 'csv')
        survey_id = kwargs.get('survey_id')

        responses = UserResponse.objects.filter(survey_id=survey_id).values(
            'user__username',
            'survey__title',
            'question__text',
            'answer__text',
            'text_response',
            'responsed_at'
        )

        df = pd.DataFrame(responses)

        if format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="survey_{survey_id}_responses.csv"'
            df.to_csv(path_or_buf=response, index=False)
            return response

        elif format == 'xlsx':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="survey_{survey_id}_responses.xlsx"'
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            return response

        else:
            return Response({'error': 'Неподдерживаемый формат'}, status=400)

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ProtectedView(APIView):
    def get(self, request):
        return Response({"message": "Это защищенный endpoint!"})

class UserResponseViewSet(viewsets.ModelViewSet):
    queryset = UserResponse.objects.all()
    serializer_class = UserResponseSerializer