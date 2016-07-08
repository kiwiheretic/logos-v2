from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import praw
import pickle
from logos.models import RoomPermissions

# Create your models here.
class RedditCredentials(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True)
    created_at = models.DateTimeField(auto_now_add = True)
    # token_data contains pickled data
    token_data= models.BinaryField()
    reddit_username = models.CharField(max_length=50, null=True)

    def credentials(self):
        data = pickle.loads(self.token_data)
        return data

    def tokens(self):
        data = pickle.loads(self.token_data)
        return [('Access Token', data['access_token']), ('Refresh Token', data['refresh_token'])]

class Subreddits(models.Model):
    name = models.CharField(max_length = 15, unique=True)
    display_name = models.CharField(max_length = 30)
    url = models.CharField(max_length=80)
    # when a subreddit record is created its usually active.  However
    # people may subsequently unsubscribe from subreddits but this
    # doesn't mean we delete all records at this point (even if everyone 
    # unsubscribes).  Hence "active" indicates if this subreddit
    # is currently in use.
    active = models.BooleanField(default=True)
    class Meta:
        ordering = ['display_name']

class MySubreddits(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True)
    subreddits = models.ManyToManyField(Subreddits, related_name='subscriptions')

class Submission(models.Model):
    name = models.CharField(max_length = 30, unique = True)
    subreddit = models.ForeignKey(Subreddits)
    created_at = models.DateTimeField(db_index=True)
    title = models.CharField(max_length = 250)
    author = models.CharField(max_length = 50)
    body = models.TextField(null=True)
    url = models.URLField()
    score = models.IntegerField(db_index = True)
    link_flair_text = models.CharField(max_length = 50, null=True)
    num_comments = models.IntegerField()
    class Meta:
        ordering = ('created_at',)

class PendingSubmissions(models.Model):
    """ Reddit submissions to be sent but dont yet have a thing ID.
    The record is to be deleted once this post has been successfully been
    verified to be on reddit"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    subreddit = models.ForeignKey(Subreddits)
    title = models.CharField(max_length = 250)
    url = models.URLField(null=True)
    body = models.TextField(null=True)
    created_at = models.DateTimeField(db_index=True)
    uploaded_at = models.DateTimeField(null=True, db_index=True)

class Comments(models.Model):
    name = models.CharField(max_length = 30, unique = True)
    submission = models.ForeignKey(Submission)
    parent_thing = models.CharField(max_length = 30)
    created_at = models.DateTimeField(db_index=True)
    author = models.CharField(max_length = 50)
    body = models.TextField()
    score = models.IntegerField(db_index = True)

class FeedProgress(models.Model):
    """ Feedi Subreddit tracking for a Subscription (FeedSub) """
    # we use ForeignKey here rather than one to one field
    # because we have a feed progress record for every subreddit
    # that is part of the original feed subscription
    feed = models.ForeignKey('FeedSub')
    subreddit = models.ForeignKey('Subreddits')
    # processed = keep track of last submission processed
    # can be null if no subreddits process yet
    processed_to = models.ForeignKey('Submission', null=True)
    # num posts processed
    processed = models.IntegerField(default=0)
    class Meta:
        unique_together = ('feed', 'subreddit')

class FeedSub(models.Model):
    """ Feed Subscription """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    frequency = models.IntegerField()
    subreddits = models.ManyToManyField(Subreddits, related_name='feeds')
    target_sub = models.ForeignKey(Subreddits, null=True)
    target_irc = models.ForeignKey(RoomPermissions, null=True)
    post_limit = models.IntegerField(default=1)
    start_date = models.DateTimeField()
    last_processed = models.DateTimeField(null=True)
    active = models.BooleanField(default = False)

