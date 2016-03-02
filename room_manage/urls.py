# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url

# required to set an app name to resolve 'url' in templates with namespacing
app_name = "rm"

urlpatterns = patterns('room_manage.views',
    url(r'^index/$', 'index', name='index'),
)
