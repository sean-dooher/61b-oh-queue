from rest_framework import serializers
from rest_framework import routers

from .models import Ticket, TicketEvent

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('student', 'status', 'assignment', 'question', 'location', 'description', 'created', 'updated')

class TicketEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketEvent
        fields = ('time', 'ticket', 'user', 'event_type')
