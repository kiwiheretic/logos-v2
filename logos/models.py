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

class NetworkPermissions(models.Model):    
    network = models.TextField()
    class Meta:
        permissions = (
            ('net_admin', 'Create user logins and assign permissions'),
            ('join_or_part_room', 'Join or part bot to rooms'),
            ('irc_cmd', 'Issue arbitrary command to bot'),
            ('set_pvt_version', 'Set bible version default in private chat window'),
            ('change_pvt_trigger', 'Set trigger used in private chat window'),
            
        )
                
class RoomPermissions(models.Model):
    network = models.TextField()
    room = models.TextField()
    class Meta:
        permissions = (
            ('room_admin', 'Assign permissions to existing users of own room'),
            ('change_trigger', 'Change trigger'),
            ('set_default_translation', 'Set default room translation'),
            ('set_verse_limits', 'Set room verse limits'),
            ('set_greeting', 'Set room greeting message'),
            ('can_speak', 'Speak through bot'),
            ('start_game', 'Can start scripture game'),
        )
        
class Plugins(models.Model):
    name = models.TextField()
    description = models.TextField()
    # currently each bot instance handles exactly one IRC network
    network = models.TextField()
    loaded = models.BooleanField(default=False)
    
class RoomPlugins(models.Model):
    plugin = models.ForeignKey('Plugins')
    network = models.TextField()
    room = models.TextField()    
    enabled = models.BooleanField(default=False)
    
class Scriptures(models.Model):
    ref = models.TextField()
    verse = models.TextField()
    
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


    