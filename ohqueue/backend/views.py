from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework import permissions

from .serializers import TicketSerializer, TicketEventSerializer
from .models import Ticket, TicketEvent, TicketStatus

from rest_framework.viewsets import ModelViewSet, ViewSet

class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.is_staff

class TicketList(ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsStaff]

class TicketQueue(ModelViewSet):
    queryset = Ticket.objects.filter(status=TicketStatus.pending.value)
    serializer_class = TicketSerializer
    permission_classes = [IsStaff]

class TicketEventList(ModelViewSet):
    queryset = TicketEvent.objects.all()
    serializer_class = TicketEventSerializer
    permission_classes = [IsStaff]
