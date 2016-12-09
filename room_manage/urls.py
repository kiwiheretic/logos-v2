# urls.py
from __future__ import absolute_import

from django.conf.urls import include, url
import room_manage.views

# required to set an app name to resolve 'url' in templates with namespacing
app_name = "rm"

urlpatterns = [
    url(r'^index/$', room_manage.views.index, name='index'),
    url(r'^site-setup/$', room_manage.views.site_setup),
    url(r'^user-setup/$', room_manage.views.user_setup),
]
