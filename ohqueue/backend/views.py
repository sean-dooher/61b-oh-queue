import json

from django.shortcuts import get_object_or_404

from rest_framework import permissions, generics, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import TicketSerializer, StaffTicketSerializer, TicketEventSerializer
from .models import Ticket, TicketEvent, TicketStatus, TicketEventType, ProfileType
from .utils import get_earliest_object_or_404

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

class TicketQueue(ReadOnlyModelViewSet):
    """
    Lists all tickets currently able to be assigned
    """
    queryset = Ticket.objects.filter(status=TicketStatus.pending.value)
    serializer_class = TicketSerializer
    permission_classes = [IsStaff]

class TicketEventList(ReadOnlyModelViewSet):
    """
    Lists all TicketEvents (for statistical purposes)
    """
    queryset = TicketEvent.objects.all()
    serializer_class = TicketEventSerializer
    permission_classes = [IsTeachingAssistant]

class StudentTicket(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    """
    Student accessible API for managing their own tickets.
    """
    serializer_class = TicketSerializer
    open_statuses = [TicketStatus.pending.value, TicketStatus.assigned.value]

    def ticket_exists(self):
        return self.get_queryset().exists()

    def get_queryset(self):
        return Ticket.objects.filter(
                    student=self.request.user.profile,
                    status__in=StudentTicket.open_statuses)

    def get_object(self):
        return get_object_or_404(self.get_queryset())

    def get(self, request, *args, **kwargs):
        """
        get:
        Returns the users current ticket.
        """
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        post:
        Creates a new user ticket, deleting the users active ticket if it exists. Needs assignment, question, description, and location.
        """
        if self.ticket_exists():
            self.get_object().delete()

        return self.create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        patch:
        Changes certain attributes of the ticket model. Needs one or more of all the fields.
        """
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        put:
        Changes certain attributes of the ticket model. Needs all of the fields.
        """
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        delete:
        Marks the users ticket as deleted.
        """
        return self.destroy(request, *args, **kwargs)

class StaffTicket(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    """
    Allows staff to mark tickets as resolved, assigned, or deleted.
    """
    permission_classes = [IsStaff]
    serializer_class = StaffTicketSerializer
    lookup_url_kwarg = 'id'
    queryset = Ticket.objects.all()

    def get_object(self):
        if (self.lookup_url_kwarg in self.kwargs and
            self.kwargs[self.lookup_url_kwarg] == 'next'):
            return self.get_next_ticket_in_queue()
        else:
            return super().get_object()

    def get_next_ticket_in_queue(self):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(status=TicketStatus.pending.value)
        return get_earliest_object_or_404(queryset)

    def get(self, request, *args, **kwargs):
        """
        get:
        Returns the users current ticket.
        """
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        f"""
        put:
        Changes the status of this ticket. Status must be one of the following {", ".join([status.value for status in TicketStatus])}.
        """
        ticket = self.get_object()
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        delete:
        Marks the users ticket as deleted.
        """
        return self.destroy(request, *args, **kwargs)

class TicketList(ReadOnlyModelViewSet):
    """
    Lists all tickets ever created
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsTeachingAssistant]
