# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url
import bibleapp.views

# required to set an app name to resolve 'url' in templates with namespacing
app_name = "bibleapp"

urlpatterns = [
#    url(r'^$', 'list'),
    url(r'^user-settings/$', bibleapp.views.user_settings, name='user_setup'),
]
