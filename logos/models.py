from __future__ import unicode_literals
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

import datetime


class BotsRunning(models.Model):
    pid = models.IntegerField()
    started = models.DateTimeField(auto_now_add=True)
    rpc = models.IntegerField()

class OptionLabels(models.Model):
    # group label - useful for extractimg only a specific group of fields
    group = models.CharField(max_length=15)
    display_order = models.PositiveSmallIntegerField()
    # form field label
    label = models.CharField(max_length=40)
    option_name = models.CharField(max_length=15)

class UserOptions(models.Model):
    namespace = models.CharField(max_length=250)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    option = models.CharField(max_length=50)
    value = models.CharField(max_length=200, null=True, blank=True)

class RoomOptions(models.Model):
    network = models.TextField()
    room = models.TextField()
    option = models.TextField()
    value = models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'room_options'


class Settings(models.Model):
    option = models.TextField()
    value = models.TextField(null=True, blank=True)

