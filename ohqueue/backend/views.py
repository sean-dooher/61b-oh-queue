import json

from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from rest_framework import permissions, generics, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import TicketSerializer, TicketEventSerializer
from .models import Ticket, TicketEvent, TicketStatus, TicketEventType, ProfileType

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

class StudentTicket(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.CreateModelMixin,
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
            self.get_object().remove(request.user.profile)

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
        self.get_object().remove(request.user.profile)
        return Response({'detail': 'Not found.'}, status=204)

class TicketList(ReadOnlyModelViewSet):
    """
    Lists all tickets ever created
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsTeachingAssistant]

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
