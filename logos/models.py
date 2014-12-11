# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals
from django.core.urlresolvers import reverse

from django.db import models
from django.conf import settings

import datetime

class BibleTranslations(models.Model):
    name = models.CharField(unique=True, max_length=10)
    class Meta:
        db_table = 'bible_translations'

class BibleBooks(models.Model):
    trans_id = models.ForeignKey('BibleTranslations')
    book_idx = models.IntegerField()
    long_book_name = models.TextField()
    canonical = models.TextField(blank=True)
    class Meta:
        db_table = 'bible_books'

class BibleVerses(models.Model):
    trans_id = models.ForeignKey('BibleTranslations')
    book = models.ForeignKey('BibleBooks')
    chapter = models.IntegerField()
    verse = models.IntegerField()
    verse_text = models.TextField()
    class Meta:
        db_table = 'bible_verses'
        index_together = [
            ["trans_id", "book", "chapter", "verse"],
        ]

class BibleConcordance(models.Model):
    trans_id = models.ForeignKey('BibleTranslations')
    book = models.ForeignKey('BibleBooks')
    chapter = models.IntegerField()
    verse = models.IntegerField()
    word_id = models.IntegerField()
    word = models.CharField(max_length=60)
    class Meta:
        db_table = 'bible_concordance'
        index_together = [
            ["trans_id", "book", "chapter", "verse", "word_id"],
            ["trans_id", "word"],
            ["trans_id", "word", "chapter"],
            ["trans_id", "word", "chapter", "verse"],
        ]

class BibleDict(models.Model):
    strongs = models.CharField(db_index=True, max_length=10)
    description = models.TextField(blank=True)
    class Meta:
        db_table = 'bible_dict'


class BibleColours(models.Model):
    network = models.TextField()
    room = models.TextField()
    element = models.TextField()
    mirc_colour = models.TextField()
    class Meta:
        db_table = 'bible_colours'

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
    
    
class Scriptures(models.Model):
    idx = models.IntegerField()
    submitter = models.TextField()
    ref = models.TextField()
    scripture_text = models.TextField()

#class BotRequests(models.Model):
#    network = models.TextField()
#    room = models.TextField()
#    password = models.TextField()
#    user = models.ForeignKey(settings.AUTH_USER_MODEL)
#    approved = models.BooleanField(default=False)

#    def get_approval_url(self):
#        return reverse('logos.views.bot_approval', args=[str(self.id)])
#    def get_deny_url(self):
#        return reverse('logos.views.bot_deny', args=[str(self.id)])

class Bots(models.Model):
    network = models.TextField()
    room = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    password = models.TextField()
    
class GameGames(models.Model):
    game_datetime = models.TextField(blank=True)
    ref = models.TextField(blank=True)
    scripture = models.TextField(blank=True)
    num_rounds = models.TextField(blank=True)
    winner = models.ForeignKey('GameUsers')

    class Meta:
        managed = False
        db_table = 'game_games'


class GameSolveAttempts(models.Model):
    game = models.ForeignKey('GameGames')
    attempt_id = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey('GameUsers')
    attempt = models.TextField(blank=True)
    reason = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'game_solve_attempts'


class GameUsers(models.Model):
    game = models.ForeignKey('GameGames')
    nick = models.TextField(blank=True)
    host = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'game_users'
    