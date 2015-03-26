# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import models
from django.core.urlresolvers import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(blank=True, default=datetime.now)
    position = models.IntegerField(blank=True, default=0, db_index=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __unicode__(self):
        return self.name


class Forum(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(blank=True, default=datetime.now)
    category = models.ForeignKey('pybb.Category', related_name='forums')
    position = models.IntegerField(blank=True, default=0, db_index=True)
    topic_count = models.IntegerField(blank=True, default=0)
    post_count = models.IntegerField(blank=True, default=0)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pybb:forum_page', args=[self.pk])


class Topic(models.Model):
    name = models.CharField(u'Topic Title', max_length=100)
    created = models.DateTimeField(blank=True, default=datetime.now)
    forum = models.ForeignKey('pybb.Forum', related_name='topics')
    post_count = models.IntegerField(blank=True, default=0)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pybb:topic_page', args=[self.pk])


class Post(models.Model):
    created = models.DateTimeField(blank=True, default=datetime.now)
    topic = models.ForeignKey('pybb.Topic', related_name='posts')
    content = models.TextField(u'Post')
    content_html = models.TextField(blank=True)
    user = models.ForeignKey('auth.User')

    def __unicode__(self):
        return self.topic.name


import pybb.signals
