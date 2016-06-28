from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import praw
import pickle

# Create your models here.
class RedditCredentials(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True)
    created_at = models.DateTimeField(auto_now_add = True)
    # token_data contains pickled data
    token_data= models.BinaryField()

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

class PendingSubmissions(models.Model):
    """ Reddit submissions to be sent but dont yet have a thing ID.
    The record is to be deleted once accepted by reddit."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True)
    subreddit = models.ForeignKey(Subreddits)
    title = models.CharField(max_length = 250)
    body = models.TextField()

class Comments(models.Model):
    name = models.CharField(max_length = 30, unique = True)
    submission = models.ForeignKey(Submission)
    parent_thing = models.CharField(max_length = 30)
    created_at = models.DateTimeField(db_index=True)
    author = models.CharField(max_length = 50)
    body = models.TextField()
    score = models.IntegerField(db_index = True)


