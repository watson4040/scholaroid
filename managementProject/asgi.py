
"""
ASGI configuration for managementProject.

This application supports normal HTTP requests and Django Channels
WebSocket connections.
"""

import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "managementProject.settings",
)

# Initialize Django before importing application routing.
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()


from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.conf import settings

from messagingApp.routing import websocket_urlpatterns


# ==========================================================
# ASGI APPLICATION
# ==========================================================

if settings.WEBSOCKETS_ENABLED:

    websocket_application = AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    )

    application = ProtocolTypeRouter(
        {
            "http": django_asgi_app,
            "websocket": websocket_application,
        }
    )

else:

    # HTTP-only fallback when WebSockets are disabled.
    application = django_asgi_app
