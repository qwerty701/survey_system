from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import ChatMessage
from .serializers import ChatMessageSerializer

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.survey_id = self.scope["url_route"]["kwargs"]["survey_id"]
        self.group_name = f"chat_{self.survey_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        user = self.scope["user"]

        if user.is_authenticated:
            message = content.get("message")
            if message:

                chat_message = ChatMessage.objects.create(
                    survey_id=self.survey_id, user=user, message=message
                )


                serializer = ChatMessageSerializer(chat_message)
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "chat_message",
                        "message": serializer.data,
                    },
                )
        else:
            await self.close()

    async def chat_message(self, event):
        await self.send_json(event["message"])