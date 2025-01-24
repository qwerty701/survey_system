from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from apps.notifications.models import Notification

User = get_user_model()

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        message = content.get("message")
        notification_type = content.get("notification_type", "custom")
        user_id = content.get("user_id")

        if not user_id:
            await self.send_json({"error": "User ID is required"})
            return

        try:
            user = await self.get_user(user_id)
        except ObjectDoesNotExist:
            await self.send_json({"error": f"User with id {user_id} does not exist"})
            return

        await self.save_notification(user, message, notification_type)

        await self.send_json({"message": "Notification created", "content": content})

    async def send_notification(self, event):
        await self.send_json(event["notification"])

    @sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"User with id {user_id} does not exist.")

    @sync_to_async
    def save_notification(self, user, message, notification_type):
        Notification.objects.create(
            user=user,
            message=message,
            notification_type=notification_type,
        )