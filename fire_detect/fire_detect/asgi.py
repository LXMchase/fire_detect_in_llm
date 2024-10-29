import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.consumers import MessageConsumer  # 导入消费者
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fire_detect.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                path("ws/messages/", MessageConsumer.as_asgi()),  # WebSocket 路由
            ]
        )
    ),
})