from __future__ import absolute_import

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

# Import the plugin you wish to test
from .bot_plugin import PrayerPlugin
from .models import Prayer

# Subclass your test class from LogosTestCase
from bot.testing.utils import LogosTestCase

class TestPrayer(LogosTestCase):
    # set plugin_class to the actual class
    # of the plugin you wish to test
    plugin_class = PrayerPlugin
    def setUp(self):
        self.fred = self.create_user('fred', "fred@noemail.com", "password1")

    def testPrayers(self):
        self.assign_network_permission('fred', 'bot_admin')
        self.set_nick("fred")
        self.login("password1")

        output = self.plugin.send_command("set straightforward pms on")
        self.assertIn('Straightforwards pms set to on', output)

        output = self.plugin.send_command("get straightforward pms")
        self.assertIn('Straightforwards pms currently set to on', output)

        output = self.plugin.send_command("set expiry days 12")
        self.assertIn('Expiry days set to 12', output)

        output = self.plugin.send_command("get expiry days")
        self.assertIn('Number of days before expiring prayers = 12', output)

        output = self.plugin.send_command("pray for my coming exam")
        self.assertIn('Prayer request successfully recorded', output)

        output = self.plugin.send_command("list")
        self.assertIn('exam', output)

        prayer = Prayer(network = self.network,
                room = self.room,
                timestamp = timezone.now() - timedelta(days=13),
                nick = "Joe",
                request = "old prayer request")
        prayer.save()

        prayer = Prayer(network = self.network,
                room = self.room,
                timestamp = timezone.now() - timedelta(days=11),
                nick = "Jane",
                request = "new prayer request")
        prayer.save()

        output = self.plugin.send_method("on_timer")
        output = self.plugin.send_command("list")
        self.assertNotIn('old', output)
        self.assertIn('new', output)

    def tearDown(self):
        self.fred.delete()
