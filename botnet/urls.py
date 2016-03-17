# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from .views import site_setup

# required to set an app name to resolve 'url' in templates with namespacing
app_name = "botnet"

urlpatterns = patterns('botnet.views',
    url(r'^site-setup/$', 'site_setup'),
    url(r'^site-setup/(?P<group>\d+)/$', 'site_setup', name='groups'),
#    url(r'^user-setup/$', 'user_setup', name='user_setup'),
)
