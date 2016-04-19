# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from .views import site_setup

# required to set an app name to resolve 'url' in templates with namespacing
app_name = "weather"

urlpatterns = patterns('weather.views',
    url(r'^site-setup/$', 'site_setup'),
)
