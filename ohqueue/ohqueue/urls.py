from django.conf.urls import url, include
from django.urls import path, include
from django.contrib import admin

from rest_framework.documentation import include_docs_urls
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

from frontend.views import index
from backend.views import StudentTicket, StaffTicket, TicketList, TicketQueue, TicketEventList
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  

router = routers.SimpleRouter()
router.register('tickets', TicketList, 'Ticket List')
router.register('queue', TicketQueue, 'Ticket Queue')
router.register('events', TicketEventList, 'Event')

api_urls = [
    path(r'', include(router.urls)),
    path(r'myticket/', StudentTicket.as_view()),
    path(r'staffticket/<id>', StaffTicket.as_view())
]

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'', index, name='index'),
    path(r'api/', include(api_urls)),
    path(r'docs/', include_docs_urls(title='OH Queue API'))
]

urlpatterns += staticfiles_urlpatterns()