from channels.generic.websocket import AsyncJsonWebsocketConsumer

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # self.user = self.scope["user"]
        #
        # if self.user.is_authenticated:
        #     self.group_name = f"notifications_{self.user.id}"
        #     await self.channel_layer.group_add(self.group_name, self.channel_name)
        #     await self.accept()
        # else:
        #     await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        pass

    async def send_notification(self, event):
        await self.send_json(event["notification"])