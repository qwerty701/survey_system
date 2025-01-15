from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Survey, Question, Answer, UserResponse

import pandas as pd
from django.http import HttpResponse


class SubmitResponseView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        survey_id = request.data.get('survey_id')
        question_id = request.data.get('question_id')
        answer_id = request.data.get('answer_id')
        text_response = request.data.get('text_response', None)

        try:
            survey = Survey.objects.get(id=survey_id)
            question = Question.objects.get(id=question_id)
            answer = Answer.objects.get(id=answer_id) if answer_id else None


            UserResponse.objects.create(
                user=user,
                survey=survey,
                question=question,
                answer=answer,
                text_response=text_response
            )

            return Response({'message': 'Ответ успешно сохранен'}, status=status.HTTP_201_CREATED)

        except Survey.DoesNotExist:
            return Response({'error': 'Опрос не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Question.DoesNotExist:
            return Response({'error': 'Вопрос не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Answer.DoesNotExist:
            return Response({'error': 'Вариант ответа не найден'}, status=status.HTTP_404_NOT_FOUND)


class ExportResponsesView(APIView):
    def get(self, request, *args, **kwargs):
        format = request.query_params.get('format', 'csv')

        responses = UserResponse.objects.all().values(
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
            response['Content-Disposition'] = 'attachment; filename="user_responses.csv"'
            df.to_csv(path_or_buf=response, index=False)
            return response

        elif format == 'xlsx':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="user_responses.xlsx"'
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