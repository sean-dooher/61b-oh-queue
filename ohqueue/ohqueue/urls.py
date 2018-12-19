from django.conf.urls import url, include
from django.urls import path, include
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

from frontend.views import index
from backend.views import TicketList, TicketQueue, TicketEventList

router = routers.SimpleRouter()
router.register('tickets', TicketList, 'Ticket')
router.register('queue', TicketQueue, 'Ticket')
router.register('events', TicketEventList, 'Event')

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'', index, name='index'),
    path(r'api/', include(router.urls))
]

urlpatterns = format_suffix_patterns(urlpatterns)