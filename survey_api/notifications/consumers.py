# notifications/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_group_name = f'notifications_{self.user.id}'

        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Отключаемся от группы
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Получаем уведомление из группы и отправляем его клиенту
    async def send_notification(self, event):
        message = event['message']
        notification_type = event['type']

        # Отправляем уведомление клиенту
        await self.send(text_data=json.dumps({
            'type': notification_type,
            'message': message,
        }))

    async def notify_survey_creation(self, event):
        survey_title = event['survey_title']
        user_id = event['user_id']
        message = f"Опрос '{survey_title}' успешно создан!"

        # Отправляем уведомление
        await self.send(text_data=json.dumps({
            'type': 'survey_creation',
            'message': message,
            'user_id': user_id,
        }))