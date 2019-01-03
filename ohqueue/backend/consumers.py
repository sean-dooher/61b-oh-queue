import logging

from .models import Ticket, TicketStatus, TicketEvent, TicketEventType
from .serializers import AnonymizedTicketSerializer, TicketEventSerializer, TicketSerializer
from .utils import ObserverBinding

from channelsmultiplexer import AsyncJsonWebsocketDemultiplexer

logger = logging.getLogger(__name__)

class TicketQueueConsumer(ObserverBinding):
    model = Ticket
    serializer_class = AnonymizedTicketSerializer
    valid_statuses = [TicketStatus.pending.value, TicketStatus.assigned.value]

    def filter_model(self, action, instance):
        return action == 'create' and instance.status in self.valid_statuses

    def get_queryset(self):
        return Ticket.objects.filter(status__in=self.valid_statuses)

class TicketEventConsumer(ObserverBinding):
    model = TicketEvent
    serializer_class = TicketEventSerializer

    def get_queryset(self):
        return TicketEvent.objects.all()

class APIDemux(AsyncJsonWebsocketDemultiplexer):
    applications = {
        "queue": TicketQueueConsumer,
        "events": TicketEventConsumer,
    }
