"""
ASGI config for Tennis Team Website backend.

This module contains the ASGI application used by Django's ASGI server
and any production ASGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` command with --asgi mode uses this.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import tennis_backend.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tennis_backend.settings')

# Standard Django ASGI application
application = get_asgi_application()

# For WebSocket support (real-time notifications)
# Uncomment and configure when ready
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             tennis_backend.routing.websocket_urlpatterns
#         )
#     ),
# })