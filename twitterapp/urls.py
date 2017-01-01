# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url
import twitterapp.views

# required to set an app name to resolve 'url' in templates with namespacing
app_name = "twitter"

urlpatterns = [
    url(r'^site-setup/$', twitterapp.views.site_setup),
]
