# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from .views import site_setup


urlpatterns = patterns('reddit.views',
#    url(r'^$', 'list'),
    url(r'^site-setup/$', 'site_setup'),
    url(r'^user-setup/$', 'user_setup', name='user_setup'),
    url(r'^authorise/$', 'authorise'),
    url(r'^discard-tokens/$', 'discard_tokens'),
    url(r'^oauth-callback/$', 'oauth_callback'),
    url(r'^my-subreddits$', 'my_subreddits'),
)
