# scripture_game models

from django.db import models

# Create your models here.
   
class GameGames(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    ref = models.TextField(blank=True)
    scripture = models.TextField(blank=True)
    num_rounds = models.TextField(blank=True)
    winner = models.ForeignKey('GameUsers', null=True)


class GameSolveAttempts(models.Model):
    game = models.ForeignKey('GameGames')
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('GameUsers')
    attempt = models.TextField(blank=True)
    reason = models.TextField(blank=True)


class GameUsers(models.Model):
    game = models.ForeignKey('GameGames')
    nick = models.TextField(blank=True)
    host = models.TextField(blank=True)

