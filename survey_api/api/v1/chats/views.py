from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.chats.models import ChatMessage
from apps.chats.serializers import ChatMessageSerializer

class ChatMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, survey_id):
        messages = ChatMessage.objects.filter(survey_id=survey_id).order_by("timestamp")
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)