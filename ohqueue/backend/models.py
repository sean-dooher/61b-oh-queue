import logging
from enum import Enum

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.utils import timezone

logger = logging.getLogger(__name__)


class ModelEnum(Enum):
    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]


class ProfileType(ModelEnum):
    student="student"
    lab_assistant="lab_assistant"
    teaching_assistant="teaching_assistant"


class Profile(models.Model):
    user = models.OneToOneField(User, models.CASCADE)

    profile_type = models.CharField(
                max_length=64,
                choices=ProfileType.choices(),
                default=ProfileType.student.value,
                db_index=True)

    def __str__(self):
        return f"{self.name} -- {self.profile_type}"


class TicketStatus(ModelEnum):
    pending="pending"
    assigned="assigned"
    resolved="resolved"
    deleted="deleted"


class Ticket(models.Model):
    created = models.DateTimeField(auto_now=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=TicketStatus.choices(), db_index=True, help_text=_("current status of this ticket"))

    student = models.ForeignKey(Profile, related_name="tickets", on_delete=models.CASCADE, db_index=True, help_text=_("student who opened this ticket"))
    assignment = models.CharField(max_length=255, help_text=_("assignment the student is requesting help with"))
    question = models.CharField(max_length=255, help_text=_("question on the assignment the student is requesting help with"))
    location = models.CharField(max_length=255, help_text=_("location of the student"))

    description = models.TextField(help_text=_("description of the problem the student has"))
    helper = models.ForeignKey(Profile, related_name="helping", null=True, on_delete=models.SET_NULL, db_index=True, help_text=_("which staff member is currently assisting the student"))

    def assign(self, helper):
        self.status = TicketStatus.assigned.value
        self.save()

        TicketEvent.objects.create(
            event_type=TicketEventType.assign.value, 
            ticket=self, user=helper
        )
    
    def remove(self, user):
        self.status = TicketStatus.deleted.value
        self.save()

        TicketEvent.objects.create(
            event_type=TicketEventType.delete.value, 
            ticket=self, user=user
        )
    
    def requeue(self, user):
        self.status = TicketStatus.pending.value
        self.save()

        TicketEvent.objects.create(
            event_type=TicketEventType.unassign.value, 
            ticket=self, user=user
        )
    
    def resolve(self, user):
        self.status = TicketStatus.resolved.value
        self.save()

        TicketEvent.objects.create(
            event_type=TicketEventType.resolve.value, 
            ticket=self, user=user
        )

    def edit(self, user, update_dict):
        good_params = ['assignment', 'question', 'description', 'location']
        for param in update_dict:
            if param in good_params:
                setattr(self, param, update_dict[param])
        
        try:
            self.save()
            TicketEvent.objects.create(
                event_type=TicketEventType.describe.value,
                ticket=self, user=user
            )
        except ValidationError as e:
            return False

        return True

    def __str__(self):
        return f"{self.student.name} -- {self.assignment}-{self.question} ({self.location}, {self.created.strftime('%Y-%m-%d %H:%M:%S')})"


class TicketEventType(ModelEnum):
    create='create'
    assign='assign'
    unassign='unassign'
    resolve='resolve'
    delete='delete'
    describe='describe'


class TicketEvent(models.Model):
    time = models.DateTimeField(auto_now=True)
    event_type = models.CharField(max_length=20, choices=TicketEventType.choices(), db_index=True)

    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Ticket {self.ticket.id}: {self.event_type} -- {self.user.name}"
