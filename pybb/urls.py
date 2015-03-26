# -*- coding: utf-8 -*-
#from django.conf.urls.defaults import *
from django.conf.urls import patterns, url, include
urlpatterns = patterns('pybb.views',
    url(r'^$', 'home_page', name='home_page'),
    url(r'^forum/(\d+)$', 'forum_page', name='forum_page'),
    url(r'^topic/(\d+)$', 'topic_page', name='topic_page'),
    url(r'^post/add$', 'post_add', name='post_add'),
    url(r'^topic/add$', 'topic_add', name='topic_add'),
    url(r'^topic/(\d+)/delete$', 'topic_delete', name='topic_delete'),
)
