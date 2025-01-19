

from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.utils import json

from chats.models import User
from surveys.models import Survey


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.survey_id = self.scope['url_route']['kwargs']['survey_id']
        self.room_group_name = f'chat_{self.survey_id}'

        # Проверка авторизации
        if not self.scope['user'].is_authenticated:
            raise DenyConnection("Unauthorized")

        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            user_id = text_data_json['user_id']

            # Проверяем существование пользователя и опроса
            user = await User.objects.aget(id=user_id)
            survey = await Survey.objects.aget(id=self.survey_id)

            # Сохраняем сообщение
            await ChatMessage.objects.acreate(
                survey=survey,
                user=user,
                message=message,
            )

            # Отправляем сообщение в группу
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': user.id,
                    'username': user.username,
                }
            )
        except User.DoesNotExist:
            await self.send(json.dumps({"error": "User does not exist"}))
        except Survey.DoesNotExist:
            await self.send(json.dumps({"error": "Survey does not exist"}))
        except Exception as e:
            await self.send(json.dumps({"error": str(e)}))