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

class Posts(models.Model):
    name = models.CharField(max_length = 30, unique = True)
    subreddit = models.ForeignKey(Subreddits)
    created_at = models.DateTimeField()
    title = models.CharField(max_length = 250)
    body = models.TextField()
    url = models.URLField()
    score = models.IntegerField()
    link_flair_text = models.CharField(max_length = 50, null=True)
    num_comments = models.IntegerField()


