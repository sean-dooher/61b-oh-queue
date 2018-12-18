import logging
from enum import Enum

from django.db import models

logger = logging.getLogger(__name__)

class Profile(models.Model):
    user = models.OneToOneField('User', models.CASCADE)

    is_staff = models.BooleanField()
    name = models.CharField(max_length=255)


class TicketStatus(Enum):
    pending="pending"
    assigned="assigned"
    resolved="resolved"
    deleted="deleted"


class Ticket(models.Model):
    created = models.DateTimeField(auto_now=True, index=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=[(tag, tag.value) for tag in TicketStatus], index=True)

    student = models.ForeignKey('User', on_delete=models.CASCADE, index=True)
    assignment = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    description = models.TextField()
    helper = models.ForeignKey('User', on_delete=models.SET_NULL, index=True)


class TicketEventType(Enum):
    create='create'
    assign='assign'
    unassign='unassign'
    resolve='resolve'
    delete='delete'
    describe='describe'


class TicketEvent(models.Model):
    time = models.DateTimeField(auto_now=True)
    event_type = models.CharField(max_length=20, choices=[(tag, tag.value) for tag in TicketEventType], index=True)

    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.SET_NULL)
