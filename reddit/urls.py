# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from .views import site_setup
from .generic_views import FeedFormView, FeedUpdateFormView

app_name = 'reddit'

urlpatterns = patterns('reddit.views',
#    url(r'^$', 'list'),
    url(r'^site-setup/$', 'site_setup', name='site_setup'),
    url(r'^user-setup/$', 'user_setup', name='user_setup'),
    url(r'^authorise/$', 'authorise', name='authorise'),
    url(r'^discard-tokens/$', 'discard_tokens', name='discard_tokens'),
    url(r'^oauth-callback/$', 'oauth_callback', name='oauth_callback'),
    url(r'^my-subreddits$', 'my_subreddits', name='mysubreddits'),
    url(r'^new-post/$', 'new_post', name='new_post'),
    url(r'^pending-posts/$', 'pending_posts', name='pending_posts'),
    url(r'^feed-add/$', FeedFormView.as_view(), name='feed-add'),
    url(r'^feed-update/(\d+)/$', FeedUpdateFormView.as_view(), name='feed-update'),
    url(r'^subreddit-feed-delete/(\d+)/$', 'delete_feed', name='delete_feed'),
    url(r'^list-subreddit-posts/([^/]+)/$', 'list_posts', name='list_posts'),
    url(r'^post-detail/(\d+)/$', 'post_detail', name='post_detail'),
    url(r'^comment-replies/([^/]+)/$', 'comment_replies', name='comment_replies'),
)
