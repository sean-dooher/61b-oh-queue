import json

from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from rest_framework import permissions
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

class StudentTicket(APIView):
    html_method_names = ['get', 'put', 'post', 'options', 'delete']
    open_statuses = [TicketStatus.pending.value, TicketStatus.assigned.value]

    def get(self, request):
        ticket = Ticket.objects.filter(
                    student=request.user.profile,
                    status__in=StudentTicket.open_statuses)

        if not ticket.exists():
            return Response(status=404)
        
        return Response(TicketSerializer(ticket.first()).data)

    def post(self, request):
        ticket = Ticket.objects.filter(
                    student=request.user.profile,
                    status__in=StudentTicket.open_statuses)

        if ticket.exists():
            response = {
                'success': False,
                'reason': 'You can only submit one ticket at a time.'
            }
            return Response(response, status=409)
        
        if request.content_type == "application/json":
            try:
                post_data = json.loads(request.body)
            except json.decoder.JSONDecodeError:
                response = {
                    'success': False,
                    'reason': 'Invalid JSON input'
                }
                return Response(response, status=400)
        else:
            post_data = request.POST
        
        missing_params = []
        for required_param in ['assignment', 'question', 'description', 'location']:
            if required_param not in post_data:
                missing_params.append(required_param)
        
        if len(missing_params) > 0:
            response = {
                'success': False,
                'reason': 'You are missing one or more required parameters.',
                'missing': missing_params
            }
            return Response(response, status=400)

        assignment = post_data['assignment']
        question = post_data['question']
        description = post_data['description']
        location = post_data['location']

        ticket = Ticket.objects.create(
            student = request.user.profile,
            status = TicketStatus.pending.value,
            assignment = assignment,
            question = question,
            description = description,
            location = location
        )

        TicketEvent.objects.create(
            ticket=ticket,
            user=request.user.profile,
            event_type=TicketEventType.create.value
        )
        
        return Response({'success': True})

    def patch(self, request):
        ticket = Ticket.objects.filter(
                    student=request.user.profile,
                    status__in=StudentTicket.open_statuses)

        if not ticket.exists():
            response = {
                'success': False,
                'reason': 'You must submit a ticket before editing it.'
            }
            return Response(response, status=404)
        
        if request.content_type == "application/json":
            try:
                patch_data = json.loads(request.body)
            except json.decoder.JSONDecodeError:
                response = {
                    'success': False,
                    'reason': 'Invalid JSON input'
                }
                return Response(response, status=400)
        else:
            patch_data = request.data
        
        ticket = ticket.first()
        success = ticket.edit(request.user.profile, patch_data)

        return Response({'success': success})

    def put(self, request):
        return self.patch(request)

    def delete(self, request):
        ticket = Ticket.objects.filter(
                    student=request.user.profile,
                    status__in=StudentTicket.open_statuses)

        if not ticket.exists():
            response = {
                'success': False,
                'reason': 'You must submit a ticket before editing it.'
            }
            return Response(response, status=404)
        
        ticket = ticket.first()
        ticket.remove(request.user.profile)

        response = {'success': True}
        return Response(response)

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
