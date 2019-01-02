import pytest
import logging
import json

from channels.testing import WebsocketCommunicator
from ohqueue.routing import application
from django.test import Client

from .sync_tests import TestUtils

logging.disable(logging.ERROR)

class ConsumerTests(TestUtils):
    @pytest.yield_fixture(autouse=True)
    async def disconnect(self):
        to_disconnect = []
        yield to_disconnect
        for client in to_disconnect:
            await client.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestLeaves(ConsumerTests):
    async def test_student_ticket(self, disconnect):
        client = WebsocketCommunicator(application, "api/")

