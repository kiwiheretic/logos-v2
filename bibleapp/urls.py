# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url

# required to set an app name to resolve 'url' in templates with namespacing
app_name = "bibleapp"

urlpatterns = patterns('bibleapp.views',
#    url(r'^$', 'list'),
    url(r'^user-settings/$', 'user_settings', name='user_setup'),
)
