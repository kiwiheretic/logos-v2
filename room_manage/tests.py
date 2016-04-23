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

        self.fred = self.create_user('fred', "fred@noemail.com", "password1")

    def testAka(self):
        self.assign_room_permission('fred', self.room, 'room_admin')
        self.set_nick("fred")
        self.login("password1")

        self.set_host('splat@fiasco.pants.com')
        output = self.plugin.send_command("aka splat")
        self.assertIn('splat is also kiwiheretic', output)

        self.set_host('jake@banana.pants.com')
        output = self.plugin.send_command("aka jake")
        self.assertIn('No other nicks for jake', output)

    def testHosts(self):
        self.assign_room_permission('fred', self.room, 'room_admin')
        self.set_nick("fred")
        self.login("password1")
        output = self.plugin.send_command("hosts splat")
        self.assertIn('nowhere', output)
        self.assertIn('fiasco', output)


    def tearDown(self):
        self.fred.delete()
        NickHistory.objects.all().delete()
