# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from .generic_views import PrayersListView, PrayerDeleteView

app_name = 'prayers'

urlpatterns = patterns('',
    url(r'^$', PrayersListView.as_view(), name='list'),
    url(r'delete/(?P<pk>\d+)/$', PrayerDeleteView.as_view(), name='delete'),
)
