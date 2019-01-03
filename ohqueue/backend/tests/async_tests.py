import pytest
import logging
import json

from channels.testing import WebsocketCommunicator
from ohqueue.routing import application
from django.test import Client

from .sync_tests import TestUtils
from backend.models import Ticket, TicketStatus, TicketEvent, TicketEventType

logging.disable(logging.ERROR)

class ConsumerTests(TestUtils):
    @pytest.yield_fixture(autouse=True)
    async def disconnect(self):
        to_disconnect = []
        yield to_disconnect
        for client in to_disconnect:
            await client.disconnect()

    async def create_client(self, user, disconnect):
        client = WebsocketCommunicator(application, "api/")

        connected, subprotocol = await client.connect()
        assert connected

        client.scope['user'] = user

        disconnect.append(client)
        return client

    async def subscribe(self, client, stream, action='all'):
        await client.send_json_to({
            "stream": stream,
            "payload": {
                "action": "subscribe",
                "data": {"action": action}
            }
        })

        await client.receive_nothing()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestLeaves(ConsumerTests):
    async def test_ticket_create(self, profile, disconnect):
        client = await self.create_client(profile.user, disconnect)
        await self.subscribe(client, 'queue', 'create')

        ticket = Ticket.objects.create(
            status=TicketStatus.assigned.value,
            student=profile,
            assignment="Project 3",
            question="Question 1",
            location="Morgan 255",
            description="[Conceptual] Need help with make client"
        )

        response = await client.receive_json_from()

        assert response['stream'] == 'queue'
        assert response['payload']['action'] == 'create'

    async def test_ticket_no_update(self, profile, disconnect):
        ticket = Ticket.objects.create(
            status=TicketStatus.pending.value,
            student=profile,
            assignment="Project 3",
            question="Question 1",
            location="Morgan 255",
            description="[Conceptual] Need help with make client"
        )

        client = await self.create_client(profile.user, disconnect)
        await self.subscribe(client, 'queue', 'all')

        ticket.status = TicketStatus.assigned.value
        ticket.save()

        assert await client.receive_nothing(), await client.receive_json_from()
