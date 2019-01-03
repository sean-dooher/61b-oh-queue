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
        client = WebsocketCommunicator(application, "api/queue")
        
        connected, subprotocol = await client.connect()
        assert connected
        
        client.scope['user'] = user

        disconnect.append(client)
        return client

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestLeaves(ConsumerTests):
    async def test_ticket_create(self, profile, disconnect):
        client = await self.create_client(profile.user, disconnect)

        ticket = Ticket.objects.create(
            status=TicketStatus.assigned.value,
            student=profile,
            assignment="Project 3",
            question="Question 1",
            location="Morgan 255",
            description="[Conceptual] Need help with make client"
        )

        response = await client.receive_json_from()

        assert False, response
