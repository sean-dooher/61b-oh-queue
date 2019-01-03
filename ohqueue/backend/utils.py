from django.http import Http404
from django.shortcuts import _get_queryset
from django.db.models.signals import post_save, post_delete
from channels.generic.websocket import AsyncJsonWebsocketConsumer

import asyncio

def get_latest_object_or_404(klass, *args, **kwargs):
    """
    Uses get().latest() to return object, or raises a Http404 exception if
    the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.filter(*args, **kwargs).latest()
    except queryset.model.DoesNotExist:
        raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)

def get_earliest_object_or_404(klass, *args, **kwargs):
    """
    Uses get().latest() to return object, or raises a Http404 exception if
    the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.filter(*args, **kwargs).earliest()
    except queryset.model.DoesNotExist:
        raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)

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
    def __init__(self, *args, **kwargs):
        self.subscribe_create = True
        self.subscribe_delete = True
        self.subscribe_update = True
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

    def post_save_receiver(self, instance, created, **kwargs):
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
        if self.subscribe_delete:
            serializer = self.serializer_class(instance)
            create_or_use_loop(self.send_json({
                'action': 'delete',
                'data': serializer.data
            }))

    def get_instance(self, pk):
        return self.get_queryset().get(pk=pk)

    def get_queryset(self):
        return EmptyQuerySet()

    def receive_json(self, content):
        if 'action' not in content:
            return

        if content['action'] == 'subscribe':
            self.handle_subscribe(content.get('data', {}))
        elif content['action'] == 'retrieve':
            self.handle_retrieve(content.get('data', {}))
        elif content['action'] == 'list':
            self.handle_list()

    def handle_retrieve(self, message):
        if 'pk' in message:
            instance = self.get_instance(message['pk'])
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
