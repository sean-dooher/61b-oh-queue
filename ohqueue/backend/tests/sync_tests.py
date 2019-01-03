import string
import random
import pytest
import logging
import json

from django.contrib.auth.models import User
from rest_framework.test import APIClient

from backend.models import Profile, ProfileType, Ticket, TicketEvent, TicketStatus, TicketEventType
from backend.serializers import TicketEventSerializer, TicketSerializer

from .utils import TestUtils

logging.disable(logging.ERROR)

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

    def test_ticket_end_to_end_single(self, profile, staff_client, ticket):
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

    def test_ticket_event_end_to_end(self, staff_client, profile, ticket):
        TicketEvent.objects.create(event_type=TicketEventType.delete.value, ticket=ticket, user=profile)

        result = staff_client.get('/api/events/')
        assert result.status_code == 200, "Should have succeeded"

        data = result.json()

        assert len(data) == 1, "Should be exactly one ticket event"
        event_json = data[0]

        self.check_single_event(event_json, ticket, profile)

@pytest.mark.django_db(transaction=True)
class TestQueue(TestUtils):
    def test_queue_single_item(self, staff_client, ticket):
        result = staff_client.get('/api/queue/')
        assert result.status_code == 200, "Should have succeeded"

        data = result.json()

        assert len(data) == 1, "Should be exactly one ticket"

    def test_queue_some_resolved(self, staff_client, tickets):
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
        response = client.get('/api/myticket/')
        assert response.status_code == 404, response.content

    def test_student_ticket_create_json(self, profile, client):
        ticket_json = self.ticket_json()
        response = client.post('/api/myticket/', json.dumps(ticket_json), content_type='application/json')
        assert response.status_code == 201, response.content

        ticket = Ticket.objects.filter(student=profile, status=TicketStatus.pending.value)
        assert ticket.exists(), "Ticket should exist after creation"

        ticket = ticket.first()

        for attr in ticket_json:
            assert getattr(ticket, attr) == ticket_json[attr], 'Expected all attributes to match'

    def test_student_ticket_create(self, profile, client):
        ticket_json = self.ticket_json()
        response = client.post('/api/myticket/', ticket_json)
        assert response.status_code == 201, response.content

        ticket = Ticket.objects.filter(student=profile, status=TicketStatus.pending.value)
        assert ticket.exists(), "Ticket should exist after creation"

        ticket = ticket.first()

        for attr in ticket_json:
            assert getattr(ticket, attr) == ticket_json[attr], 'Expected all attributes to match'

    def test_student_ticket_double_create(self, profile, client):
        ticket_json = self.ticket_json()
        response = client.post('/api/myticket/', ticket_json)

        for key in ticket_json:
            ticket_json[key] += '-new'

        response = client.post('/api/myticket/', ticket_json)

        ticket = Ticket.objects.filter(student=profile, status=TicketStatus.deleted.value)
        assert ticket.exists(), "Old ticket should have been deleted"

        ticket = Ticket.objects.filter(student=profile, status=TicketStatus.pending.value)
        assert ticket.exists(), "Ticket should exist after creation"

        ticket = ticket.first()

        for attr in ticket_json:
            assert getattr(ticket, attr) == ticket_json[attr], 'Expected all attributes to match'

    def test_student_ticket_double_create_view(self, profile, client):
        client.post('/api/myticket/', self.ticket_json())
        client.post('/api/myticket/', self.ticket_json())

        response = client.get('/api/myticket/')
        assert response.status_code == 200, response.content

    def test_student_ticket_create_event(self, profile, client):
        response = client.post('/api/myticket/', self.ticket_json())
        assert response.status_code == 201, response.content

        ticket_event = TicketEvent.objects.filter(event_type=TicketEventType.create.value)
        assert ticket_event.exists(), "Ticket event should have been created"

    def test_student_ticket_create_bad_json(self, profile, client):
        response = client.post('/api/myticket/', '{"bad":13', content_type='application/json')
        assert response.status_code == 400, response.content

    def test_student_ticket_view(self, profile, client):
        ticket_json = self.ticket_json()
        client.post('/api/myticket/', ticket_json)

        response = client.get('/api/myticket/')
        assert response.status_code == 200, response.content

        ticket = response.json()

        for attr in ticket_json:
            assert ticket[attr] == ticket_json[attr], 'Expected all attributes to match'

    def test_student_ticket_delete(self, profile, client):
        client.post('/api/myticket/', self.ticket_json())

        response = client.delete('/api/myticket/')
        assert response.status_code == 204, response.content

        ticket = Ticket.objects.filter(student=profile, status=TicketStatus.deleted.value)
        assert ticket.exists(), "Ticket should exist with deletion status"

    def test_student_ticket_delete_event(self, profile, client):
        client.post('/api/myticket/',  self.ticket_json())
        client.delete('/api/myticket/')

        ticket_event = TicketEvent.objects.filter(event_type=TicketEventType.delete.value)
        assert ticket_event.exists(), "Ticket event should have been created"

    def test_student_ticket_delete_view(self, profile, client):
        client.post('/api/myticket/', self.ticket_json())
        client.delete('/api/myticket/')

        response = client.get('/api/myticket/')
        assert response.status_code == 404, response.content

    def test_student_ticket_patch_full(self, profile, client):
        ticket_json = self.ticket_json()
        response = client.post('/api/myticket/', ticket_json)

        for key in ticket_json:
            ticket_json[key] = ticket_json[key] + '-updated'

        response = client.patch('/api/myticket/', ticket_json)
        assert response.status_code == 200, response.content

        ticket = Ticket.objects.filter(student=profile, status=TicketStatus.pending.value)
        assert ticket.exists(), "Ticket should exist after creation"

        ticket = ticket.first()

        for attr in ticket_json:
            assert getattr(ticket, attr) == ticket_json[attr], 'Expected all attributes to match'

    def test_student_ticket_patch_partial(self, profile, client):
        ticket_json = self.ticket_json()
        response = client.post('/api/myticket/', ticket_json)
        assert response.status_code == 201, response.content

        ticket_json['location'] = ticket_json['location'] + '-updated'
        ticket_update = {'location': ticket_json['location']}

        response = client.patch('/api/myticket/', ticket_update)
        assert response.status_code == 200, response.content

        ticket = Ticket.objects.filter(student=profile, status=TicketStatus.pending.value)
        assert ticket.exists(), "Ticket should exist after creation"

        ticket = ticket.first()

        for attr in ticket_json:
            assert getattr(ticket, attr) == ticket_json[attr], 'Expected all attributes to match'

    def test_student_ticket_patch_event(self, profile, client):
        response = client.post('/api/myticket/', self.ticket_json())

        ticket_update = {'location': 'new_location'}

        response = client.patch('/api/myticket/', ticket_update)
        ticket = Ticket.objects.filter(student=profile, status=TicketStatus.pending.value)

        ticket_event = TicketEvent.objects.filter(ticket=ticket.first(), event_type=TicketEventType.describe.value)
        assert ticket_event.exists(), "Ticket event should have been created"


@pytest.mark.django_db(transaction=True)
class TestStaffApi(TestUtils):
    def resolve_ticket(self, ticket):
        ticket.status = TicketStatus.resolved.value
        ticket.save()

        return ticket

    def test_staff_null_get_by_id(self, staff_client, ticket):
        result = staff_client.get(f'/api/staffticket/{ticket.id + 1}')
        assert result.status_code == 404, result.content

    def test_staff_null_get_by_next(self, staff_client):
        result = staff_client.get('/api/staffticket/next')
        assert result.status_code == 404, result.content

    def test_staff_single_item_get_by_id(self, staff_client, ticket):
        result = staff_client.get(f'/api/staffticket/{ticket.id}')
        assert result.status_code == 200, result.content

    def test_staff_single_item_get_by_id(self, staff_client, ticket):
        result = staff_client.get(f'/api/staffticket/{ticket.id}')
        assert result.status_code == 200, result.content

    def test_staff_get_next_resolve(self, staff_client, tickets):
        ticket1_json = staff_client.get('/api/staffticket/next').json()
        self.resolve_ticket(Ticket.objects.get(id=ticket1_json['id']))

        ticket2_json = staff_client.get('/api/staffticket/next').json()

        assert ticket2_json['id'] != ticket1_json['id']

    def test_staff_put_next_assigned(self, staff_client, tickets):
        result = staff_client.put('/api/staffticket/next', {'status': TicketStatus.assigned.value})
        assert result.status_code == 200, result.content
        ticket = Ticket.objects.get(id=result.json()['id'])

        assert TicketStatus(ticket.status) == TicketStatus.assigned

    def test_staff_put_next_assigned_multiple(self, staff_client, tickets):
        for _ in range(4):
            result = staff_client.put('/api/staffticket/next', {'status': TicketStatus.assigned.value})
            assert result.status_code == 200, result.content
            ticket = Ticket.objects.get(id=result.json()['id'])

            assert TicketStatus(ticket.status) == TicketStatus.assigned

        result = staff_client.get('/api/queue/')
        assert result.status_code == 200, "Should have succeeded"

        data = result.json()

        assert len(data) == 6, "Should be exactly 6 tickets in queue (4 assigned)"

    def test_staff_put_next_assigned_multiple(self, staff_client, tickets):
        for _ in range(4):
            result = staff_client.put('/api/staffticket/next', {'status': TicketStatus.assigned.value})
            assert result.status_code == 200, result.content
            ticket = Ticket.objects.get(id=result.json()['id'])

            assert TicketStatus(ticket.status) == TicketStatus.assigned

        result = staff_client.get('/api/queue/')
        assert result.status_code == 200, "Should have succeeded"

        data = result.json()

        assert len(data) == 6, "Should be exactly 6 tickets in queue (4 assigned)"

    def test_staff_assign_ticket_helper(self, staff_profile, staff_client, tickets):
        result = staff_client.put('/api/staffticket/next', {'status': TicketStatus.assigned.value})
        ticket = Ticket.objects.get(id=result.json()['id'])

        assert ticket.helper == staff_profile

    def test_staff_assign_ticket_event(self, staff_client, tickets):
        result = staff_client.put('/api/staffticket/next', {'status': TicketStatus.assigned.value})
        ticket = Ticket.objects.get(id=result.json()['id'])

        assert TicketEvent.objects.filter(ticket=ticket, event_type=TicketEventType.assign.value).exists()

    def test_staff_delete_ticket_event(self, staff_client, tickets):
        result = staff_client.put('/api/staffticket/next', {'status': TicketStatus.deleted.value})
        ticket = Ticket.objects.get(id=result.json()['id'])

        assert TicketEvent.objects.filter(ticket=ticket, event_type=TicketEventType.delete.value).exists()

    def test_staff_unassign_ticket_event(self, staff_client, tickets):
        result = staff_client.put('/api/staffticket/next', {'status': TicketStatus.assigned.value})
        ticket = Ticket.objects.get(id=result.json()['id'])
        result = staff_client.put(f'/api/staffticket/{ticket.id}', {'status': TicketStatus.pending.value})

        assert TicketEvent.objects.filter(ticket=ticket, event_type=TicketEventType.unassign.value).exists()

    def test_staff_resolve_ticket_event(self, staff_client, tickets):
        result = staff_client.put('/api/staffticket/next', {'status': TicketStatus.assigned.value})
        ticket = Ticket.objects.get(id=result.json()['id'])
        result = staff_client.put(f'/api/staffticket/{ticket.id}', {'status': TicketStatus.resolved.value})

        assert TicketEvent.objects.filter(ticket=ticket, event_type=TicketEventType.resolve.value).exists()

    def test_staff_reassign_ticket_event(self, staff_client, tickets):
        result = staff_client.put('/api/staffticket/next', {'status': TicketStatus.assigned.value})
        ticket = Ticket.objects.get(id=result.json()['id'])


        staff_profile = User.objects.create_user("staff2", email="test@test.com", password="pass123").profile
        staff_profile.profile_type = ProfileType.teaching_assistant.value
        staff_profile.save()

        staff2_client = APIClient()
        staff2_client.login(username="staff2", password="pass123")

        result = staff2_client.put(f'/api/staffticket/{ticket.id}', {'status': TicketStatus.assigned.value})

        assert TicketEvent.objects.filter(ticket=ticket, event_type=TicketEventType.unassign.value).exists()
