# urls.py
from __future__ import absolute_import

from django.conf.urls import patterns, include, url
#from .generic_views import FeedFormView, FeedUpdateFormView, CommentsListView, SubmissionsListView, CommentsDeleteView
import reddit.views
import reddit.generic_views

app_name = 'reddit'

urlpatterns = [
#    url(r'^$', 'list'),
    url(r'^site-setup/$', reddit.views.site_setup, name='site_setup'),
    url(r'^user-setup/$', reddit.views.user_setup, name='user_setup'),
    url(r'^authorise/$', reddit.views.authorise, name='authorise'),
    url(r'^discard-tokens/$', reddit.views.discard_tokens, name='discard_tokens'),
    url(r'^oauth-callback/$', reddit.views.oauth_callback, name='oauth_callback'),
    url(r'^my-subreddits$', reddit.views.my_subreddits, name='mysubreddits'),
    url(r'^new-post/$', reddit.views.new_post, name='new_post'),
    url(r'^pending-posts/$', reddit.generic_views.SubmissionsListView.as_view(), name='pending_posts'),
    url(r'^pending-comments/$', reddit.generic_views.CommentsListView.as_view(), name='pending_comments'),
    url(r'^delete-pending-comments/(?P<pk>\d+)/$', reddit.generic_views.CommentsDeleteView.as_view(), name='delete_pending_comments'),
    url(r'^feed-add/$', reddit.generic_views.FeedFormView.as_view(), name='feed-add'),
    url(r'^feed-update/(\d+)/$', reddit.generic_views.FeedUpdateFormView.as_view(), name='feed-update'),
    url(r'^subreddit-feed-delete/(\d+)/$', reddit.views.delete_feed, name='delete_feed'),
    url(r'^list-subreddit-posts/([^/]+)/$', reddit.views.list_posts, name='list_posts'),
    url(r'^post-detail/(\d+)/$', reddit.views.post_detail, name='post_detail'),
    url(r'^comment-replies/([^/]+)/$', reddit.views.comment_replies, name='comment_replies'),
    url(r'^submit-reply/([^/]+)/$', reddit.views.submit_reply, name='submit_reply'),
]
