from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Feed(models.Model):
    feedurl = models.URLField(unique=True)
    active = models.BooleanField(default=True)

class FeedSubscription(models.Model):
    network = models.CharField(null=False, max_length=50)
    room = models.CharField(null=False, max_length=50)
    user_added = models.ForeignKey(User)
    feed = models.ForeignKey(Feed)
    periodic = models.CharField(blank=True, default="", max_length=15)
    active = models.BooleanField(default=True)

class Cache(models.Model):
    feed = models.ForeignKey(Feed)
    guid = models.CharField(unique=True, max_length=80)
    link = models.URLField(null=False)
    title = models.CharField(null=False, max_length=200)
    description = models.TextField(null=True)
    published = models.DateTimeField()


class CacheViews(models.Model):
    network = models.CharField(null=False, max_length=50)
    room = models.CharField(null=False, max_length=50)
    cache = models.ForeignKey(Cache)
