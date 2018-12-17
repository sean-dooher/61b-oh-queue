import json
import logging

from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from guardian.shortcuts import assign_perm, remove_perm
from guardian.models import Group as PermGroup

logger = logging.getLogger(__name__)

class BasicConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass
