from django.urls import re_path

from .consumer import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/<str:room_name>/',
            ChatConsumer),
]
