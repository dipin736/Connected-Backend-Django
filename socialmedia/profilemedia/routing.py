from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<user_id>\d+)/(?P<target_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/online/(?P<user_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
]
