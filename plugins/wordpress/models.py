# model for twitter plugin

from django.db import models
from django.contrib.auth.models import User

class WPCredentials(models.Model):
    user = models.ForeignKey(User) 
    username = models.CharField(max_length=60)
    password = models.CharField(max_length=60)
    url = models.CharField(max_length=200, null=True)
    class Meta:
        app_label = 'logos'
        
            