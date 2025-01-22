from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.survey_id = self.scope['url_route']['kwargs']['survey_id']
            self.room_group_name = f'chat_{self.survey_id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        except Exception as e:
            print(f"Error during connection: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"Error during disconnect: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data['message']
            sender_id = data['sender_id']

            chatroom = await self.get_chatroom()
            if chatroom:
                await self.save_message(chatroom, sender_id, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': sender_id
                }
            )
        except Exception as e:
            print(f"Error during message receive: {e}")
            raise StopConsumer()

    async def chat_message(self, event):
        try:
            message = event['message']
            sender_id = event['sender_id']
            await self.send(text_data=json.dumps({
                'message': message,
                'sender_id': sender_id
            }))
        except Exception as e:
            print(f"Error during message send: {e}")