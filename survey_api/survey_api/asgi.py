import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'survey_api.settings')

django_asgi_app = get_asgi_application()

from chats.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from notifications.routing import websocket_urlpatterns as notifications_websocket_urlpatterns

websocket_urlpatterns = chat_websocket_urlpatterns + notifications_websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})