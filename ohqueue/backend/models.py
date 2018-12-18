import logging
from enum import Enum

from django.db import models
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class Profile(models.Model):
    user = models.OneToOneField(User, models.CASCADE)

    is_staff = models.BooleanField()
    name = models.CharField(max_length=255)


class TicketStatus(Enum):
    pending="pending"
    assigned="assigned"
    resolved="resolved"
    deleted="deleted"


class Ticket(models.Model):
    created = models.DateTimeField(auto_now=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=[(tag, tag.value) for tag in TicketStatus], db_index=True)

    student = models.ForeignKey(Profile, related_name="tickets", on_delete=models.CASCADE, db_index=True)
    assignment = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    description = models.TextField()
    helper = models.ForeignKey(Profile, related_name="helping", null=True, on_delete=models.SET_NULL, db_index=True)


class TicketEventType(Enum):
    create='create'
    assign='assign'
    unassign='unassign'
    resolve='resolve'
    delete='delete'
    describe='describe'


class TicketEvent(models.Model):
    time = models.DateTimeField(auto_now=True)
    event_type = models.CharField(max_length=20, choices=[(tag, tag.value) for tag in TicketEventType], db_index=True)

    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
