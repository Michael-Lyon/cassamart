import json
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Messages


User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
        else:
            self.user_id = self.scope["user"].id
            self.room_name = self.scope['url_route']['kwargs']['room_slug']
            self.room_group_name = f'chat_{self.room_name}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # room = text_data_json["current_room"]

        # message = await database_sync_to_async(Messages.objects.create)(
        #     sender=self.scope['user'].id,
        #     message=message,
        #     room=room
        # )

        # send message to room group
        await (self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.message,
                'user': self.scope['user'].id,
                "date": str(message.date)
            }
        )

    # receive message from room group

    async def chat_message(self, event):
        # Send message to WebSocket
       await self.send(text_data=json.dumps(event))
       
       
