from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Feed(models.Model):
    network = models.CharField(max_length=50)
    room = models.CharField(max_length=50)
    user_added = models.ForeignKey(User)
    feedurl = models.URLField()
    periodic = models.CharField(blank=True, default="", max_length=15)
    active = models.BooleanField(default=True)
