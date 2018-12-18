from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from frontend.views import index
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'', index, name='index')
]

urlpatterns = format_suffix_patterns(urlpatterns)