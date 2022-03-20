# scripture_game models

from django.db import models

# Create your models here.
   
class GameGames(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    ref = models.TextField(blank=True)
    scripture = models.TextField(blank=True)
    num_rounds = models.TextField(blank=True)
    winner = models.ForeignKey('GameUsers', null=True, on_delete = models.CASCADE)


class GameSolveAttempts(models.Model):
    game = models.ForeignKey('GameGames', on_delete = models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('GameUsers', on_delete = models.CASCADE)
    attempt = models.TextField(blank=True)
    reason = models.TextField(blank=True)


class GameUsers(models.Model):
    game = models.ForeignKey('GameGames', on_delete = models.CASCADE)
    nick = models.TextField(blank=True)
    host = models.TextField(blank=True)

