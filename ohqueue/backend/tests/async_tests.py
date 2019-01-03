import pytest
import logging
import json

from channels.testing import WebsocketCommunicator
from ohqueue.routing import application
from django.test import Client

from .sync_tests import TestUtils
from backend.models import Ticket, TicketStatus, TicketEvent, TicketEventType
from backend.models import ticket_status_to_event

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

        assert await client.receive_nothing()

    async def test_event_create(self, profile, disconnect):
        client = await self.create_client(profile.user, disconnect)
        await self.subscribe(client, 'events', 'create')

        ticket = Ticket.objects.create(
            status=TicketStatus.pending.value,
            student=profile,
            assignment="Project 3",
            question="Question 1",
            location="Morgan 255",
            description="[Conceptual] Need help with make client"
        )

        event = TicketEvent.objects.create(
            event_type=TicketEventType.create.value,
            ticket=ticket, user=profile
        )

        response = await client.receive_json_from()

        assert response['stream'] == 'events'
        assert response['payload']['action'] == 'create'

    @pytest.mark.parametrize("status", TicketStatus)
    async def test_event_emission(self, status, profile, staff_client, tickets, disconnect):
        client = await self.create_client(profile.user, disconnect)
        await self.subscribe(client, 'events', 'all')

        result = staff_client.put('/api/staffticket/next', {'status': status.value})
        ticket = Ticket.objects.get(id=result.json()['id'])

        event_types = [status.value for status in ticket_status_to_event(TicketStatus.pending, status)]

        for _ in event_types:
            response = await client.receive_json_from()
            ticket_event = response['payload']['data']

            assert ticket_event['ticket'] == ticket.id
            assert ticket_event['event_type'] in event_types

        assert await client.receive_nothing()

    async def test_event_emission_resolve(self, profile, staff_client, tickets, disconnect):
        client = await self.create_client(profile.user, disconnect)
        await self.subscribe(client, 'events', 'all')

        result = staff_client.put('/api/staffticket/next', {'status': TicketStatus.assigned.value})
        ticket = Ticket.objects.get(id=result.json()['id'])

        response = await client.receive_json_from()
        ticket_event = response['payload']['data']

        assert ticket_event['ticket'] == ticket.id
        assert ticket_event['event_type'] == TicketEventType.assign.value

        result = staff_client.put(f'/api/staffticket/{ticket.id}', {'status': TicketStatus.resolved.value})

        response = await client.receive_json_from()
        ticket_event = response['payload']['data']

        assert ticket_event['ticket'] == ticket.id
        assert ticket_event['event_type'] == TicketEventType.resolve.value

        assert await client.receive_nothing()
