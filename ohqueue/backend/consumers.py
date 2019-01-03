import logging
import asyncio

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channelsmultiplexer import AsyncJsonWebsocketDemultiplexer
from django.db.models.signals import post_save, post_delete

from .models import Ticket, TicketStatus, TicketEvent, TicketEventType
from .serializers import AnonymizedTicketSerializer, TicketEventSerializer, TicketSerializer

logger = logging.getLogger(__name__)

def create_or_use_loop(awaitable):
    """
    This function is a hacky fix to allow the test runner to work with
    the ObserverBinding class. As otherwise the observer would have to
    use async_to_sync, which works in production, but has conflicts with
    the testing environment.
    """
    try:
        event_loop = asyncio.get_event_loop()
    except RuntimeError:
        event_loop = None

    if event_loop and event_loop.is_running():
        event_loop.call_soon_threadsafe(event_loop.create_task, awaitable)
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(awaitable)
        finally:
            loop.close()
            asyncio.set_event_loop(event_loop)

class ObserverBinding(AsyncJsonWebsocketConsumer):
    lookup_field = 'pk'
    """
    Provides a basic binding for accessing models
    over websockets and subscribing to changes
    """
    def __init__(self, *args, **kwargs):
        self.subscribe_create = False
        self.subscribe_delete = False
        self.subscribe_update = False
        self._connect_to_model()
        super().__init__(*args, **kwargs)

    def _connect_to_model(self):
        post_save.connect(
            self.post_save_receiver,
            sender=self.model,
            dispatch_uid=id(self)
        )
        post_delete.connect(self.post_delete_receiver, sender=self.model, dispatch_uid=id(self))

    def _disconnect_from_model(self):
        post_save.disconnect(None, dispatch_uid=id(self))
        post_delete.disconnect(None, dispatch_uid=id(self))

    async def disconnect(self, message):
        self._disconnect_from_model()
        await super().disconnect(message)

    def filter_model(self, action, instance):
        """
        Allows for filtering of models in subscriptions
        """
        return True

    def post_save_receiver(self, instance, created, **kwargs):
        action = 'create' if created else 'update'
        if self.filter_model(action, instance):
            serializer = self.serializer_class(instance)
            if created and self.subscribe_create:
                create_or_use_loop(self.send_json({
                    'action': 'create',
                    'data': serializer.data
                }))
            elif self.subscribe_update:
                create_or_use_loop(self.send_json({
                    'action': 'update',
                    'data': serializer.data
                }))

    def post_delete_receiver(self, instance, **kwargs):
        if self.filter_model('delete', instance):
            if self.subscribe_delete:
                serializer = self.serializer_class(instance)
                create_or_use_loop(self.send_json({
                    'action': 'delete',
                    'data': serializer.data
                }))

    def get_instance(self, pk):
        return self.get_queryset().get(**{self.lookup_field:pk})

    def get_queryset(self):
        return EmptyQuerySet()

    async def receive_json(self, content):
        if 'action' not in content:
            return

        if content['action'] == 'subscribe':
            self.handle_subscribe(content.get('data', {}))
        elif content['action'] == 'retrieve':
            self.handle_retrieve(content.get('data', {}))
        elif content['action'] == 'list':
            self.handle_list()

    def handle_subscribe(self, message):
        if 'action' not in message:
            return

        if message['action'] in ['create', 'all']:
            self.subscribe_create = True
        if message['action'] in ['update', 'all']:
            self.subscribe_update = True
        if message['action'] in ['delete', 'all']:
            self.subscribe_delete = True

    def handle_retrieve(self, message):
        if self.lookup_field in message:
            instance = self.get_instance(message[self.lookup_field])
            serializer = self.serializer_class(instance)
            create_or_use_loop(self.send_json({
                'action': 'retrieve',
                'data': serializer.data
            }))

    def handle_list(self):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        create_or_use_loop(self.send_json({
            'action': 'list',
            'data': serializer.data
        }))


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
