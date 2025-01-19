from rest_framework import viewsets
from .models import ChatMessage
from .serializers import ChatMessageSerializer

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        survey_id = self.request.query_params.get('survey_id')
        if survey_id:
            return ChatMessage.objects.filter(survey_id=survey_id)
        return super().get_queryset()