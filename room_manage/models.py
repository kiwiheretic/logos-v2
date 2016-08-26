from django.db import models
# DateTimeField.auto_now_add *always* overrides entry data so we
# need "default = timezone.now()" instead
from django.utils import timezone

# Create your models here.
class NickHistory(models.Model):
    network = models.TextField(db_index=True)
    room = models.TextField()
    nick = models.CharField(db_index=True, max_length=40)
    host_mask = models.CharField(max_length=80)
    time_seen = models.DateTimeField(default = timezone.now, db_index=True)

class NickSummary(models.Model):
    network = models.TextField(db_index=True)
    nick = models.CharField(db_index=True, max_length=40)
    host_mask = models.CharField(max_length=80)
    last_seen = models.DateTimeField()
    class Meta:
        index_together = [
            ['network', 'nick'],
            ['network', 'host_mask']
        ]


class Probation(models.Model):
    network = models.TextField()
    room = models.TextField()
    host_mask = models.CharField(max_length=80)
    
class Penalty(models.Model):
    network = models.TextField()
    room = models.TextField()
    nick_mask = models.CharField(max_length=80)
    # The reason to be added to kick message
    reason = models.CharField(max_length=80, null=True, blank = True)
    # When penalty starts
    begin_time = models.DateTimeField(default = timezone.now)
    # when penalty ends
    end_time = models.DateTimeField(default = timezone.now)   
    # whether to kick from room whilst penalty applies
    kick = models.BooleanField(default = False)
    # whether to mute in room whilst penalty applies
    mute = models.BooleanField(default = False)
    
class NickProtection(models.Model):
    network = models.TextField()
    room = models.TextField()
    # protect if registered only
    protect_registered = models.BooleanField(default = False)
    # immune from down votes
    downvote_immunity = models.BooleanField(default = False)

# only registered nicks can down vote
class DownVotes (models.Model):
    network = models.TextField()
    room = models.TextField()
    nick_mask = models.CharField(max_length=80)
    downvoting_nick = models.CharField(max_length = 40)
    downvote_datetime = models.DateTimeField(auto_now_add=True)
