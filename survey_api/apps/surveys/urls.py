from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.v1.surveys.views import (
    CategoryViewSet,
    SurveyViewSet,
    QuestionViewSet,
    AnswerViewSet,
    SubmitResponseView,
    ExportResponsesView,
    UserResponseViewSet,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'surveys', SurveyViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'answers', AnswerViewSet)
router.register(r'user-responses', UserResponseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:survey_id>/submit-response/', SubmitResponseView.as_view(), name='submit_response'),
    path('<int:survey_id>/export/', ExportResponsesView.as_view(), name='export_responses'),
]