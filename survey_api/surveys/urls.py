# polls/urls.py

from django.urls import path
from .views import SubmitResponseView, ExportResponsesView

urlpatterns = [
    path('submit-response/', SubmitResponseView.as_view(), name='submit-response'),
    path('export-responses/', ExportResponsesView.as_view(), name='export-responses'),
]