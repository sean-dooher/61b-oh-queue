from django.urls import re_path
from channels.db import database_sync_to_async
from channelsmultiplexer import AsyncJsonWebsocketDemultiplexer

# top level routing for websockets
websocket_routing = [
]