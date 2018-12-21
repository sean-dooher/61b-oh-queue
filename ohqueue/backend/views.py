from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework import permissions

from .serializers import TicketSerializer, TicketEventSerializer
from .models import Ticket, TicketEvent, TicketStatus, ProfileType

from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet

class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        staff_types = [ProfileType.lab_assistant.value, ProfileType.teaching_assistant.value]
        user = request.user
        return user.is_authenticated and user.profile.profile_type in staff_types

class IsTeachingAssistant(permissions.BasePermission):
    def has_permission(self, request, view):
        ta_types = [ProfileType.teaching_assistant.value]
        user = request.user
        return user.is_authenticated and user.profile.profile_type in ta_types

class TicketList(ReadOnlyModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsTeachingAssistant]

class TicketQueue(ReadOnlyModelViewSet):
    queryset = Ticket.objects.filter(status=TicketStatus.pending.value)
    serializer_class = TicketSerializer
    permission_classes = [IsStaff]

class TicketEventList(ReadOnlyModelViewSet):
    queryset = TicketEvent.objects.all()
    serializer_class = TicketEventSerializer
    permission_classes = [IsTeachingAssistant]
