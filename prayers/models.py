from django.db import models

# Create your models here.
class Prayer(models.Model):
    network = models.CharField(max_length=60)
    room = models.CharField(max_length=60)
    timestamp = models.DateTimeField(auto_now_add=True)
    nick = models.CharField(max_length=90)
    request = models.CharField(max_length=200)

    def __str__(self):
        return "%s, %s" % (self.nick, self.request[:15])
