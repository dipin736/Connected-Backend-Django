import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from profilemedia.models import ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.scope_path = self.scope['path']

        self.user_id = int(self.scope['url_route']['kwargs']['user_id'])
        self.user = self.scope['user']

        # Check if it's an online tracking socket
        if "online" in self.scope_path:
            self.room_group_name = f"online_{self.user_id}"
        else:
            self.target_id = int(self.scope['url_route']['kwargs']['target_id'])
            self.room_name = f"chat_{min(self.user_id, self.target_id)}_{max(self.user_id, self.target_id)}"
            self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        print(f"[CONNECT] user={self.user}, is_authenticated={self.user.is_authenticated}")

        if self.user.is_authenticated:
            print(f"[CONNECT] ✅ User {self.user.id} is authenticated, adding to online cache...")
            await self.add_online_user(self.user.id)
        else:
            print("[CONNECT] ❌ User is anonymous — not added to online list")

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        if self.user.is_authenticated:
            await self.remove_online_user(self.user.id)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender = data.get('sender')
        receiver = data.get('receiver')
        message = data.get('message')

        # Only process if message is valid and in a chat route
        if sender and receiver and message and "chat" in self.scope_path:
            await self.save_message(sender, receiver, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender,
                    'receiver': receiver,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, sender, receiver, message):
        ChatMessage.objects.create(sender_id=sender, receiver_id=receiver, message=message)

    @database_sync_to_async
    def add_online_user(self, user_id):
        online_users = cache.get("online_users", set())
        if not isinstance(online_users, set):
            online_users = set()
        online_users.add(user_id)
        cache.set("online_users", online_users, timeout=None)
        print(f"[ONLINE] ✅ User {user_id} added to cache. Now online users: {online_users}")


    @database_sync_to_async
    def remove_online_user(self, user_id):
        online_users = cache.get("online_users", set())
        if not isinstance(online_users, set):
            online_users = set()
        online_users.discard(user_id)
        cache.set("online_users", online_users, timeout=None)

    
