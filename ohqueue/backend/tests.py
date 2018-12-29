import pytest
import logging
import json

from django.contrib.auth.models import User
from rest_framework.test import APIClient

from backend.models import Profile, ProfileType, Ticket, TicketEvent, TicketStatus, TicketEventType
from backend.serializers import TicketEventSerializer, TicketSerializer

logging.disable(logging.ERROR)

class TestUtils:
    @pytest.fixture
    def profile(self):
        self.user = User.objects.create_user("test", email="test@test.com", password="pass123")
        self.student_profile = Profile.objects.create(user=self.user, name="Alice Bobson")
        return self.student_profile

    @pytest.fixture
    def staff_profile(self):
        self.user = User.objects.create_user("staff", email="test@test.com", password="pass123")
        self.staff = Profile.objects.create(user=self.user, profile_type=ProfileType.teaching_assistant.value, name="Alice Bobson")
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

@pytest.mark.django_db(transaction=True)
class TestStudentApi(TestUtils):
    def ticket_json(self):
        return {
            'assignment': 'Project 3',
            'question': 'Question 1',
            'location': 'Morgan 255',
            'description': 'Problem with graph implementation'
        }

    def test_student_no_ticket(self, profile, client):
        response = client.get('/api/myticket')

        assert response.status_code == 404, response.json()

    def test_student_ticket_create_json(self, profile, client):
        ticket_json = self.ticket_json()
        response = client.post('/api/myticket', json.dumps(ticket_json), content_type='application/json')
        assert response.status_code == 200, response.json()

        ticket = Ticket.objects.filter(student=profile, status=TicketStatus.pending.value)
        assert ticket.exists(), "Ticket should exist after creation"

        ticket = ticket.first()

        for attr in ticket_json:
            assert getattr(ticket, attr) == ticket_json[attr], 'Expected all attributes to match'

    def test_student_ticket_create(self, profile, client):
        ticket_json = self.ticket_json()
        response = client.post('/api/myticket', ticket_json)
        assert response.status_code == 200, response.json()

        ticket = Ticket.objects.filter(student=profile, status=TicketStatus.pending.value)
        assert ticket.exists(), "Ticket should exist after creation"

        ticket = ticket.first()

        for attr in ticket_json:
            assert getattr(ticket, attr) == ticket_json[attr], 'Expected all attributes to match'

    def test_student_ticket_create_bad_json(self, profile, client):
        response = client.post('/api/myticket', '{"bad":13', content_type='application/json')
        assert response.status_code == 400, response.json()

    def test_student_ticket_view(self, profile, client):
        ticket_json = self.ticket_json()
        response = client.post('/api/myticket', ticket_json)
        assert response.status_code == 200, response.json()

        response = client.get('/api/myticket')
        assert response.status_code == 200, response.json()

        ticket = response.json()

        for attr in ticket_json:
            assert ticket[attr] == ticket_json[attr], 'Expected all attributes to match'

    def test_student_ticket_delete(self, profile, client):
        ticket_json = self.ticket_json()
        response = client.post('/api/myticket', ticket_json)
        assert response.status_code == 200, response.json()

        response = client.delete('/api/myticket')
        assert response.status_code == 200, response.json()

        ticket = Ticket.objects.filter(student=profile, status=TicketStatus.deleted.value)
        assert ticket.exists(), "Ticket should exist with deletion status"

    def test_student_ticket_delete_view(self, profile, client):
        ticket_json = self.ticket_json()
        response = client.post('/api/myticket', ticket_json)
        assert response.status_code == 200, response.json()

        response = client.delete('/api/myticket')
        assert response.status_code == 200, response.json()

        response = client.get('/api/myticket')
        assert response.status_code == 404, response.json()

    def test_student_ticket_patch_full(self, profile, client):
        ticket_json = self.ticket_json()
        response = client.post('/api/myticket', ticket_json)
        assert response.status_code == 200, response.json()

        for key in ticket_json:
            ticket_json[key] = ticket_json[key] + '-updated'

        response = client.patch('/api/myticket', ticket_json)
        assert response.status_code == 200, response.json()

        ticket = Ticket.objects.filter(student=profile, status=TicketStatus.pending.value)
        assert ticket.exists(), "Ticket should exist after creation"

        ticket = ticket.first()

        for attr in ticket_json:
            assert getattr(ticket, attr) == ticket_json[attr], 'Expected all attributes to match'

    def test_student_ticket_patch_partial(self, profile, client):
        ticket_json = self.ticket_json()
        response = client.post('/api/myticket', ticket_json)
        assert response.status_code == 200, response.json()

        ticket_json['location'] = ticket_json['location'] + '-updated'
        ticket_update = {'location': ticket_json['location']}

        response = client.patch('/api/myticket', ticket_update)
        assert response.status_code == 200, response.json()

        ticket = Ticket.objects.filter(student=profile, status=TicketStatus.pending.value)
        assert ticket.exists(), "Ticket should exist after creation"

        ticket = ticket.first()

        for attr in ticket_json:
            assert getattr(ticket, attr) == ticket_json[attr], 'Expected all attributes to match'
