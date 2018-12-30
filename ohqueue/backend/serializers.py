from rest_framework.serializers import ModelSerializer
from rest_framework import routers

from .models import Ticket, TicketEvent, TicketStatus, TicketEventType

class TicketSerializer(ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('assignment', 'question', 'location', 'description', 'student', 'status', 'created', 'updated', 'id')
        read_only_fields = ('student', 'status', 'created', 'updated', 'id')

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user.profile
        validated_data['status'] = TicketStatus.pending.value

        ticket = ModelSerializer.create(self, validated_data)

        TicketEvent.objects.create(
            ticket = ticket,
            event_type = TicketEventType.create.value,
            user = ticket.student
        )

        return ticket

    def update(self, instance, validated_data):
        ticket = ModelSerializer.update(self, instance, validated_data)
        
        TicketEvent.objects.create(
            ticket = ticket,
            event_type = TicketEventType.describe.value,
            user = self.context['request'].user.profile
        )

        return ticket

class TicketEventSerializer(ModelSerializer):
    class Meta:
        model = TicketEvent
        fields = ('time', 'ticket', 'user', 'event_type')
