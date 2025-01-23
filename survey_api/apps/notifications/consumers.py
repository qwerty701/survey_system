from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Получаем пользователя из scope
        self.user = self.scope["user"]

        # Проверяем, аутентифицирован ли пользователь
        # if self.user.is_authenticated:
        # Создаем уникальное имя группы для уведомлений пользователя
        self.group_name = f"notifications_{self.user.id}"

        # Добавляем канал в группу
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Принимаем соединение
        await self.accept()
        # else:
        #     # Закрываем соединение, если пользователь не аутентифицирован
        #     await self.close()

    async def disconnect(self, close_code):
        # Убираем канал из группы при отключении
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        # Обработка входящих сообщений (если нужно)
        await self.send_json({"message": "Received", "content": content})

    async def send_notification(self, event):
        # Отправляем уведомление клиенту
        await self.send_json(event["notification"])
