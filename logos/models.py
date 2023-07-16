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

class NetworkPermissions(models.Model):    
    network = models.TextField(unique=True)
    class Meta:
        permissions = (
            ('bot_admin', 'Create user logins and assign permissions'),
            ('activate_plugins', 'Can activate/deactivate plugins network wide'),
            ('join_or_part_room', 'Join or part bot to rooms'),
            ('irc_cmd', 'Issue arbitrary command to bot'),
            ('set_pvt_version', 'Set bible version default in private chat window'),
            ('change_pvt_trigger', 'Set trigger used in private chat window'),
            ('change_nick', 'Can issue a bot nick change command'),
            ('warn_user', 'Warn a user of their behaviour'),
            
        )
                
class RoomPermissions(models.Model):
    network = models.TextField()
    room = models.TextField()
    class Meta:
        unique_together = ('network', 'room')
        permissions = (
            ('room_admin', 'Assign permissions to existing users of own room'),
            ('change_trigger', 'Change trigger'),
            ('set_default_translation', 'Set default room translation'),
            ('set_verse_limits', 'Set room verse limits'),
            ('set_greeting', 'Set room greeting message'),
            ('can_speak', 'Speak through bot'),
            ('enable_plugins', 'Can enable or disable room plugins'),
            ('kick_user', 'Can kick user'),
            ('ban_user', 'Can ban user'),
            ('room_op', 'Bot can op'),
            ('twitter_op', 'Can add or remove twitter follows')
        )

class Plugins(models.Model):
    name = models.TextField(unique=True)
    description = models.TextField()
    system = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
        
#class NetworkPlugins(models.Model):
#    plugin = models.ForeignKey('Plugins', on_delete = models.CASCADE)
#    # currently each bot instance handles exactly one IRC network
#    network = models.TextField()
#    loaded = models.BooleanField(default=False)
#    # bot_admin disabling overrides room_admin enabling
#    enabled = models.BooleanField(default=True)
    
class RoomPlugins(models.Model):
    plugin = models.ForeignKey('Plugins', on_delete = models.CASCADE)
    room = models.TextField()    
    enabled = models.BooleanField(default=False)
   
    def __str__(self):
        return "{}:{}".format(self.plugin.name, self.room)
