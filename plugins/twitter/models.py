# model for twitter plugin

from django.db import models

class TwitterStatuses(models.Model):
    twitter_id = models.DecimalField(unique=True, max_digits=25, decimal_places=0)
    created_at = models.DateTimeField()
    screen_name = models.CharField(max_length=60)
    text = models.CharField(max_length=260)
    url = models.CharField(max_length=200, null=True)
    class Meta:
        app_label = 'logos'
        
class ReportedTweets(models.Model):
    network = models.CharField(max_length=60)
    room = models.CharField(max_length=30)
    tweet = models.ForeignKey('TwitterStatuses')
    class Meta:
        app_label = 'logos' 
        
class TwitterFollows(models.Model):
    network = models.CharField(max_length=60)
    room = models.CharField(max_length=30)
    screen_name = models.CharField(max_length=60)
    class Meta:
        app_label = 'logos'             