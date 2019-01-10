from django.conf.urls import url, include
from django.urls import path, include, re_path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  
from django.views.generic.base import RedirectView

from rest_framework.documentation import include_docs_urls
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

from frontend.views import index
from backend.views import StudentTicket, StaffTicket, TicketList, TicketQueue, TicketEventList
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
    path(r'', RedirectView.as_view(url='queue')),
    re_path(r'^queue/.*', index, name='index'),
    path(r'api/', include(api_urls)),
    path(r'docs/', include_docs_urls(title='OH Queue API'))
]

urlpatterns += staticfiles_urlpatterns()