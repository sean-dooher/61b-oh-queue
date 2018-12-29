from django.conf.urls import url, include
from django.urls import path, include
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

from frontend.views import index
from backend.views import StudentTicket, TicketList, TicketQueue, TicketEventList
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  

router = routers.SimpleRouter()
router.register('tickets', TicketList, 'Ticket')
router.register('queue', TicketQueue, 'Ticket')
router.register('events', TicketEventList, 'Event')

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'', index, name='index'),
    path(r'api/', include(router.urls)),
    path(r'api/myticket', StudentTicket.as_view())
]
urlpatterns += staticfiles_urlpatterns()

urlpatterns = format_suffix_patterns(urlpatterns)