import pytest
import logging
import json

from backend.models import Profile, Ticket, TicketEvent, TicketStatus, TicketEventType
from backend.serializers import TicketEventSerializer, TicketSerializer

from django.contrib.auth.models import User

logging.disable(logging.ERROR)

@pytest.mark.django_db(transaction=True)
class TestSerializers:
    @pytest.fixture
    def profile(self):
        self.user = User.objects.create_user("test", email="test@test.com", password="pass123")
        self.student_profile = Profile.objects.create(user=self.user, is_staff=False, name="Alice Bobson")
        return self.student_profile

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

    def test_ticket_serializer(self, profile, ticket):
        serialized = TicketSerializer(ticket)

        expected_data = {
            'status': TicketStatus.assigned.value,
            'student': profile.id,
            'assignment': 'Project 3',
            'question': 'Question 1',
            'location': 'Morgan 255',
            'description': '[Conceptual] Need help with make client'
        }

        for key in expected_data:
            assert key in serialized.data, "Missing key in serializer"
            assert expected_data[key] == serialized.data[key], "Incorrect value in serializer"

        for key in ['created', 'updated']:
            assert key in serialized.data, "Missing key in serializer"

    def test_ticket_end_to_end(self):
        pass

    def test_permissions_tickets(self):
        pass

    def test_ticket_event_serializer(self, profile, ticket):
        ticket_event = TicketEvent.objects.create(event_type=TicketEventType.delete.value, ticket=ticket, user=profile)
        serialized = TicketEventSerializer(ticket_event)

        expected_data = {
            'event_type': TicketEventType.delete.value,
            'ticket': ticket.id,
            'user': profile.id
        }

        for key in expected_data:
            assert key in serialized.data, "Missing key in serializer"
            assert expected_data[key] == serialized.data[key], "Incorrect value in serializer"

        assert 'time' in serialized.data, "Missing key in serializer"

    def test_ticket_event_end_to_end(self):
        pass
