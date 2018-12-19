import pytest
import logging
import json

from django.contrib.auth.models import User
from rest_framework.test import APIClient

from backend.models import Profile, Ticket, TicketEvent, TicketStatus, TicketEventType
from backend.serializers import TicketEventSerializer, TicketSerializer

logging.disable(logging.ERROR)

class TestUtils:
    @pytest.fixture
    def profile(self):
        self.user = User.objects.create_user("test", email="test@test.com", password="pass123")
        self.student_profile = Profile.objects.create(user=self.user, is_staff=False, name="Alice Bobson")
        return self.student_profile

    @pytest.fixture
    def staff_profile(self):
        self.user = User.objects.create_user("staff", email="test@test.com", password="pass123")
        self.staff = Profile.objects.create(user=self.user, is_staff=True, name="Alice Bobson")
        return self.staff

    @pytest.fixture
    def client(self):
        client = APIClient()
        client.login(username="test", password="pass123")
        return client

    @pytest.fixture
    def staff_client(self):
        client = APIClient()
        client.login(username="staff", password="pass123")
        return client

@pytest.mark.django_db(transaction=True)
class TestSerializers(TestUtils):
    @pytest.fixture
    def ticket(self):
        ticket = Ticket.objects.create(
            status=TicketStatus.assigned.value,
            student=self.student_profile,
            assignment="Project 3",
            question="Question 1",
            location="Morgan 255",
            description="[Conceptual] Need help with make client"
        )
        return ticket

    def check_single_ticket(self, data, profile):
        expected_data = {
            'status': TicketStatus.assigned.value,
            'student': profile.id,
            'assignment': 'Project 3',
            'question': 'Question 1',
            'location': 'Morgan 255',
            'description': '[Conceptual] Need help with make client'
        }

        for key in expected_data:
            assert key in data, "Missing key in serializer"
            assert expected_data[key] == data[key], "Incorrect value in serializer"

        for key in ['created', 'updated']:
            assert key in data, "Missing key in serializer"
    
    def check_single_event(self, data, ticket, profile):
        expected_data = {
            'event_type': TicketEventType.delete.value,
            'ticket': ticket.id,
            'user': profile.id
        }

        for key in expected_data:
            assert key in data, "Missing key in serializer"
            assert expected_data[key] == data[key], "Incorrect value in serializer"

        assert 'time' in data, "Missing key in serializer"

    def test_ticket_serializer(self, profile, ticket):
        serialized = TicketSerializer(ticket)
        self.check_single_ticket(serialized.data, profile)

    def test_ticket_end_to_end_single(self, staff_profile, profile, staff_client, ticket):
        result = staff_client.get('/api/tickets/')
        assert result.status_code == 200, "Should have succeeded"

        data = result.json()

        assert len(data) == 1, "Should be exactly one ticket"
        ticket_json = data[0]

        self.check_single_ticket(ticket_json, profile)

    def test_permissions_tickets(self, profile, client, ticket):
        result = client.get('/api/tickets/')
        assert result.status_code == 403, "Non staff user should not be able to read tickets"

    def test_ticket_event_serializer(self, profile, ticket):
        ticket_event = TicketEvent.objects.create(event_type=TicketEventType.delete.value, ticket=ticket, user=profile)
        serialized = TicketEventSerializer(ticket_event)

        self.check_single_event(serialized.data, ticket, profile)

    def test_ticket_event_end_to_end(self, staff_profile, staff_client, profile, ticket):
        TicketEvent.objects.create(event_type=TicketEventType.delete.value, ticket=ticket, user=profile)

        result = staff_client.get('/api/events/')
        assert result.status_code == 200, "Should have succeeded"

        data = result.json()

        assert len(data) == 1, "Should be exactly one ticket event"
        event_json = data[0]

        self.check_single_event(event_json, ticket, profile)

@pytest.mark.django_db(transaction=True)
class TestQueue(TestUtils):
    def create_ticket(self, status=TicketStatus.pending):
        return Ticket.objects.create(
                status=status.value,
                student=self.student_profile,
                assignment="Project 3",
                question="Question 1",
                location="Morgan 255",
                description="[Conceptual] Need help with make client")

    @pytest.fixture
    def tickets(self):
        return [self.create_ticket() for _ in range(10)]

    def test_queue_single_item(self, profile, staff_profile, staff_client):
        self.create_ticket()

        result = staff_client.get('/api/queue/')
        assert result.status_code == 200, "Should have succeeded"

        data = result.json()

        assert len(data) == 1, "Should be exactly one ticket"

    def test_queue_some_resolved(self, profile, staff_profile, staff_client, tickets):
        for i, ticket in enumerate(tickets):
            if i in [1, 2, 4]:
                ticket.status = TicketStatus.resolved.value
                ticket.save()

        result = staff_client.get('/api/queue/')
        assert result.status_code == 200, "Should have succeeded"

        data = result.json()

        assert len(data) == 7, "Should be exactly 7 tickets in queue (3 resolved)"
