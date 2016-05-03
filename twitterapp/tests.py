# tests
from __future__ import absolute_import

from django.test import TestCase

# Import the plugin you wish to test
from .bot_plugin import TwitterPlugin

# Subclass your test class from LogosTestCase
from bot.testing.utils import LogosTestCase

class TestTwitter(LogosTestCase):
    # set plugin_class to the actual class
    # of the plugin you wish to test
    plugin_class = TwitterPlugin
    def setUp(self):
        self.fred = self.create_user('fred', "fred@noemail.com", "password1")

    def testFollows(self):
        self.assign_room_permission('fred', self.room, 'twitter_op')
        self.set_nick("fred")
        self.login("password1")

        output = self.plugin.send_command("add follow {} @bible_101".format(self.room))
        self.assertIn('Twitter follow added successfully', output)

        output = self.plugin.send_command("list follows {}".format(self.room))
        self.assertIn('@bible_101', output)

        output = self.plugin.send_command("remove follow {} @bible_101".format(self.room))
        self.assertIn('Twitter follow removed successfully', output)

        output = self.plugin.send_command("list follows {}".format(self.room))
        self.assertNotIn('@bible_101', output)

    def tearDown(self):
        self.fred.delete()
