from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import chat.routing
from chat.middlewares import WebSocketJWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': WebSocketJWTAuthMiddleware(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
