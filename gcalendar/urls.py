# urls.py
from __future__ import absolute_import

from django.conf.urls import include, url
import gcalendar.views

# required to set an app name to resolve 'url' in templates with namespacing
app_name = "gcal"

urlpatterns = [
#    url(r'^$', 'list'),
    url(r'^site-setup/$', gcalendar.views.site_setup),
    url(r'^user-setup/$', gcalendar.views.user_setup, name='user_setup'),
    url(r'^callback/$', gcalendar.views.oauth_callback),
    url(r'^list/$', gcalendar.views.list, name='list'),
    url(r'^new-event/$', gcalendar.views.new_event),
    url(r'^edit-event/([^/]+)/$', gcalendar.views.edit_event, name='edit-event'),
    url(r'^event-detail/([^/]+)/$', gcalendar.views.event_detail, name='normal-delete'),
    url(r'^event-detail/([^/]+)/1/$', gcalendar.views.event_detail, {'recurrence_delete':True}, name='recurrence-delete'),
]
