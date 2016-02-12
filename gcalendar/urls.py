# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from .views import site_setup

# required to set an app name to resolve 'url' in templates with namespacing
app_name = "google_calendar"

urlpatterns = patterns('gcalendar.views',
#    url(r'^$', 'list'),
    url(r'^site-setup/$', 'site_setup'),
    url(r'^user-setup/$', 'user_setup', name='user_setup'),
    url(r'^callback/$', 'oauth_callback'),
)
