from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.middlewares import WebSocketJWTAuthMiddleware
import chat.routing
from django.core.asgi import get_asgi_application



application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': WebSocketJWTAuthMiddleware(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
