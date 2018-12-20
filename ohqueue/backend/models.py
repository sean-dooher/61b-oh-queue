import logging
from enum import Enum

from django.db import models
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class ProfileType(Enum):
    student="student"
    lab_assistant="lab_assistant"
    teaching_assistant="teaching_assistant"


class Profile(models.Model):
    user = models.OneToOneField(User, models.CASCADE)

    profile_type = models.CharField(
                max_length=64,
                choices=[(tag, tag.value) for tag in ProfileType],
                default=ProfileType.student.value,
                db_index=True)

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

    def assign(self, helper):
        Ticket.status = TicketStatus.assigned.value
        self.save()

        TicketEvent.objects.create(
            event_type=TicketEventType.assign.value, 
            ticket=self, user=helper
        )
    
    def delete(self, user):
        Ticket.status = TicketStatus.deleted.value
        self.save()

        TicketEvent.objects.create(
            event_type=TicketEventType.delete.value, 
            ticket=self, user=user
        )
    
    def requeue(self, user):
        Ticket.status = TicketStatus.pending.value
        self.save()

        TicketEvent.objects.create(
            event_type=TicketEventType.unassign.value, 
            ticket=self, user=user
        )
    
    def resolve(self, user):
        Ticket.status = TicketStatus.resolved.value
        self.save()

        TicketEvent.objects.create(
            event_type=TicketEventType.resolve.value, 
            ticket=self, user=user
        )


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
