import logging

from .models import Ticket, TicketStatus, TicketEvent, TicketEventType
from .serializers import AnonymizedTicketSerializer, TicketEventSerializer, TicketSerializer
from .utils import ObserverBinding

from channelsmultiplexer import AsyncJsonWebsocketDemultiplexer

logger = logging.getLogger(__name__)

class TicketQueueConsumer(ObserverBinding):
    """
    Allows users to view tickets in queue over a websocket
    """
    model = Ticket
    serializer_class = AnonymizedTicketSerializer
    valid_statuses = [TicketStatus.pending.value, TicketStatus.assigned.value]

    def filter_model(self, action, instance):
        """
        Prevents users from subscribing to ticket events by invalidating all models
        """
        return False

    def get_queryset(self):
        return Ticket.objects.filter(status__in=self.valid_statuses)

class TicketEventConsumer(ObserverBinding):
    """
    Allows users to subscribe to ticket event creation (to handle front end events)
    """
    model = TicketEvent
    serializer_class = TicketEventSerializer

    def get_queryset(self):
        return TicketEvent.objects.all()

class APIDemux(AsyncJsonWebsocketDemultiplexer):
    applications = {
        "queue": TicketQueueConsumer,
        "events": TicketEventConsumer,
    }
