import json
import logging

from djangochannelsrestframework.consumers import view_as_consumer
from channelsmultiplexer import AsyncJsonWebsocketDemultiplexer
from asgiref.sync import async_to_sync

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone

from .views import StudentTicket, TicketEventList

logger = logging.getLogger(__name__)

class APIDemux(AsyncJsonWebsocketDemultiplexer):
    applications = {
        "myticket": view_as_consumer(StudentTicket),
        "events": view_as_consumer(TicketEventList)
    }