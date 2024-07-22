"""
ASGI config for EasyMeal project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyMeal.settings')

# application = get_asgi_application()


import os
import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

dbfile = 'EasyMeal.settings.production'

# f = open(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/.git/HEAD", "r")
# if 'ref: refs/heads/testing' in f.read():
# 	dbfile = 'EasyMeal.settings.testing'
# f.close()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', dbfile)

django_asgi_app = get_asgi_application()

from support.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)