from django.urls import re_path
from channels.db import database_sync_to_async
from .consumers import APIDemux

# top level routing for websockets
websocket_routing = [
    re_path(r"^api/$", APIDemux),
]
