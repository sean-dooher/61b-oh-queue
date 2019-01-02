from rest_framework.serializers import ModelSerializer
from rest_framework import routers

from .models import Ticket, TicketEvent, TicketStatus, TicketEventType, ticket_status_to_event

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
        ticket = super().update(instance, validated_data)
        
        TicketEvent.objects.create(
            ticket = ticket,
            event_type = TicketEventType.describe.value,
            user = self.context['request'].user.profile
        )

        return ticket

class StaffTicketSerializer(ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('assignment', 'question', 'location', 'description', 'student', 'status', 'created', 'updated', 'id')
        read_only_fields = ('assignment', 'question', 'location', 'description', 'student', 'created', 'updated', 'id')

    def update(self, instance, validated_data):
        validated_data['helper'] = self.context['request'].user.profile

        pre_status = TicketStatus(instance.status)
        ticket = super().update(instance, validated_data)
        post_status = TicketStatus(instance.status)


        event_types = ticket_status_to_event(pre_status, post_status)
        for event_type in event_types:
            TicketEvent.objects.create(
                ticket = ticket,
                event_type = event_type.value,
                user = validated_data['helper']
            )

        return ticket

class TicketEventSerializer(ModelSerializer):
    class Meta:
        model = TicketEvent
        fields = ('time', 'ticket', 'user', 'event_type')
