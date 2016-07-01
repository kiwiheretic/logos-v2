# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from .views import site_setup
from .generic_views import FeedFormView


urlpatterns = patterns('reddit.views',
#    url(r'^$', 'list'),
    url(r'^site-setup/$', 'site_setup', name='site_setup'),
    url(r'^user-setup/$', 'user_setup', name='user_setup'),
    url(r'^authorise/$', 'authorise', name='authorise'),
    url(r'^discard-tokens/$', 'discard_tokens', name='discard_tokens'),
    url(r'^oauth-callback/$', 'oauth_callback', name='oauth_callback'),
    url(r'^my-subreddits$', 'my_subreddits', name='mysubreddits'),
    url(r'^new-post/$', 'new_post', name='new_post'),
    url(r'^feed-add/$', FeedFormView.as_view(), name='feed-add'),
    url(r'^list-subreddit-posts/([^/]+)/$', 'list_posts', name='list_posts'),
    url(r'^post-detail/(\d+)/$', 'post_detail', name='post_detail'),
)
