from django.db import models

class CapturedUrls(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    nick = models.CharField(max_length=90)
    room = models.CharField(max_length=60)
    url = models.CharField(max_length=200)
