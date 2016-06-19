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

    def tokens(self):
        data = pickle.loads(self.token_data)
        return [('Access Token', data['access_token']), ('Refresh Token', data['refresh_token'])]
