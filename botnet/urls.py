# urls.py
from __future__ import absolute_import

from django.conf.urls import include, url
import botnet.views

# required to set an app name to resolve 'url' in templates with namespacing
app_name = "botnet"

urlpatterns = [
    url(r'^site-setup/$', botnet.views.site_setup),
    url(r'^site-setup/(?P<group>\d+)/$', botnet.views.site_setup, name='groups'),
]
