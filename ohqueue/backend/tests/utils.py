import string
import random
import pytest
import logging
import json

from django.contrib.auth.models import User
from rest_framework.test import APIClient

from backend.models import Profile, ProfileType, Ticket, TicketEvent, TicketStatus, TicketEventType

class TestUtils:
    @pytest.fixture
    def profile(self):
        self.user = User.objects.create_user("test", email="test@test.com", password="pass123")
        self.student_profile = self.user.profile
        return self.student_profile

    @pytest.fixture
    def staff_profile(self):
        self.staff_user = User.objects.create_user("staff", email="test@test.com", password="pass123")
        self.staff = self.staff_user.profile
        self.staff.profile_type = ProfileType.teaching_assistant.value
        self.staff.save()
        return self.staff

    @pytest.fixture
    def client(self, profile):
        client = APIClient()
        client.login(username="test", password="pass123")
        return client

    @pytest.fixture
    def staff_client(self, staff_profile):
        client = APIClient()
        client.login(username="staff", password="pass123")
        return client

    @pytest.fixture
    def ticket(self, profile):
        return Ticket.objects.create(
                    status=TicketStatus.pending.value,
                    student=self.student_profile,
                    assignment="Project 3",
                    question="Question 1",
                    location="Morgan 255",
                    description="[Conceptual] Need help with make client")

    @pytest.fixture
    def students(self):
        self.student_profiles = []
        for _ in range(10):
            name = ''.join(random.choices(string.ascii_uppercase, k=12))
            password = ''.join(random.choices(string.ascii_uppercase, k=12))
            self.student_profiles.append(User.objects.create_user(name, password).profile)
        return self.students

    @pytest.fixture
    def tickets(self, students):
        self.student_tickets = []
        for student in self.student_profiles:
            self.student_tickets.append(
                Ticket.objects.create(
                    student=student,
                    status=TicketStatus.pending.value,
                    assignment="Project 3",
                    question="Question 1",
                    location="Morgan 255",
                    description="[Conceptual] Need help with make client"
            ))
        return self.student_tickets
