"""
ASGI config for djangoPlant project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
from django.core.asgi import get_asgi_application  # type: ignore

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoPlant.settings')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter  # type: ignore

application = ProtocolTypeRouter({
    "http": django_asgi_app,
})
