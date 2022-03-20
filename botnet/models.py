from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class BotNetGroups(models.Model):
    group_name = models.CharField(max_length=100, blank=False)
    active = models.BooleanField(default=False)

class BotNetRooms(models.Model):
    group = models.ForeignKey('BotNetGroups', on_delete = models.CASCADE)
    network = models.CharField(max_length=100)
    room = models.CharField(max_length=100)
