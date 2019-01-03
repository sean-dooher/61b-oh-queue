import logging

from .models import Ticket, TicketStatus, TicketEvent, TicketEventType
from .serializers import AnonymizedTicketSerializer, TicketEventSerializer, TicketSerializer
from .utils import ObserverBinding

logger = logging.getLogger(__name__)

class TicketQueueConsumer(ObserverBinding):
    model = Ticket
    serializer_class = AnonymizedTicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(status__in=[TicketStatus.pending.value, TicketStatus.assigned.value])
