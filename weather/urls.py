# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url
import weather.views

# required to set an app name to resolve 'url' in templates with namespacing
app_name = "weather"

urlpatterns = [
    url(r'^site-setup/$', weather.views.site_setup),
]
