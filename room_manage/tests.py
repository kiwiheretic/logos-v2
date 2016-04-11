# tests
from __future__ import absolute_import

from django.test import TestCase

# Import the plugin you wish to test
from .bot_plugin import RoomManagementPlugin

from .models import NickHistory

# Subclass your test class from LogosTestCase
from bot.testing.utils import LogosTestCase

class TestRM(LogosTestCase):
    # set plugin_class to the actual class
    # of the plugin you wish to test
    plugin_class = RoomManagementPlugin
    def setUp(self):
        n = NickHistory(nick='splat', host_mask = 'splat@nowhere.pants.com',
                network = self.network, room='#room')
        n.save()
        n = NickHistory(nick='splat', host_mask = 'splat@fiasco.pants.com',
                network = self.network, room='#room')
        n.save()
        n = NickHistory(nick='kiwiheretic', 
                host_mask = 'splat@fiasco.pants.com',
                network = self.network, room='#room')
        n.save()

        n = NickHistory(nick='Jake', 
                host_mask = 'jake@banana.pants.com',
                network = self.network, room='#room')
        n.save()

    def testAka(self):
        self.set_host('splat@fiasco.pants.com')
        output = self.plugin.send_command("aka splat")
        self.assertIn('splat is kiwiheretic', output)

        self.set_host('jake@banana.pants.com')
        output = self.plugin.send_command("aka jake")
        self.assertIn('No other nicks for jake', output)

    def testHosts(self):
        output = self.plugin.send_command("hosts splat")
        self.assertIn('nowhere', output)
        self.assertIn('fiasco', output)
