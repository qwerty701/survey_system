"""
ASGI config for survey_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chats.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from notifications import websocket_urlpatterns as notifications_websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_name.settings')

# Инициализация стандартного Django ASGI-приложения
django_asgi_app = get_asgi_application()

# Настройка маршрутов WebSocket
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat_websocket_urlpatterns + notifications_websocket_urlpatterns
        )
    ),
})

