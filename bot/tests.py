# tests
from django.utils import unittest
from django.conf import settings
from django.core import serializers

import io
import gzip
import os
#from django.test import TestCase
import pdb
import bot.plugins.bible_bot as bb
import pluginDespatch

class FakePlugin(object):
    def __init__(self, *args, **kwargs):
        self.irc_conn = self
        self._cls_list = [self]
        self.output = []
        
    def say(self, channel, message):
        self.output.append(('say', channel, message))

    def msg(self, channel, message):
        self.output.append(('msg', channel, message))

    def describe(self, channel, action):
        pass

    def notice(self, user, message):
        self.output.append(('notice', channel, message))

    def kick(self, channel, user, reason=None):    
        pass

    def mode(self, chan, set, modes, limit = None, user = None, mask = None):
        pass
                
    def sendLine(self, line):
        pass

# Monkey patch for testing only
# based on http://stackoverflow.com/questions/9646187/how-to-copy-a-member-function-of-another-class-into-myclass-in-python
FakePlugin.command = pluginDespatch.PluginDespatcher.__dict__['command']

class TestBibleBot(unittest.TestCase):
    #https://docs.djangoproject.com/en/1.7/topics/testing/tools/#topics-testing-fixtures
    #https://docs.djangoproject.com/en/dev/ref/django-admin/#database-specific-fixtures

    def setUp(self):
        # Load test data into test database
        
        fixtures_path = os.path.join(settings.BASE_DIR, 'logos', 'fixtures')
        fixture_file = os.path.join(fixtures_path, 'testdata.bibles.json.gz')
        fp = gzip.open(fixture_file)
        for ii, obj in enumerate(serializers.deserialize("json", fp)):
            if ii % 500 == 0: print ".",
            obj.save()
        print
        cls = bb.BibleBot
        # Hideous Monkey Patch for testing only
        cls.__bases__ = (FakePlugin,)
        self.plugin = cls()
        self.nick = 'testBot'
        
        self.user = "testBot!logos@Chatopia-530r0e.xtra.co.nz"
        self.chan = '#test'
        self.act = '?'
        
        self.plugin.nickname = self.nick
        self.plugin.network = 'irc.server.net'
        

    def testVerseLookup(self):
        msg = "John 3 16"
        orig_msg = self.act + msg
        self.plugin.command(self.nick, self.user, self.chan, orig_msg, msg, self.act)
        print "---"
        self.assertIn('John 3:16', self.plugin.output.pop()[2])
        
