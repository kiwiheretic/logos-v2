# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from .views import site_setup

# required to set an app name to resolve 'url' in templates with namespacing
app_name = "gcal"

urlpatterns = patterns('gcalendar.views',
#    url(r'^$', 'list'),
    url(r'^site-setup/$', 'site_setup'),
    url(r'^user-setup/$', 'user_setup', name='user_setup'),
    url(r'^callback/$', 'oauth_callback'),
    url(r'^list/$', 'list', name='list'),
    url(r'^new-event/$', 'new_event'),
    url(r'^edit-event/([^/]+)/$', 'edit_event', name='edit-event'),
    url(r'^event-detail/([^/]+)/$', 'event_detail', name='normal-delete'),
    url(r'^event-detail/([^/]+)/1/$', 'event_detail', {'recurrence_delete':True}, name='recurrence-delete'),
)
