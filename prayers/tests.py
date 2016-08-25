from __future__ import absolute_import

from django.test import TestCase

# Import the plugin you wish to test
from .bot_plugin import PrayerPlugin

# Subclass your test class from LogosTestCase
from bot.testing.utils import LogosTestCase

class TestPrayer(LogosTestCase):
    # set plugin_class to the actual class
    # of the plugin you wish to test
    plugin_class = PrayerPlugin
    def setUp(self):
        pass

    def testPrayers(self):

        output = self.plugin.send_command("pray for my coming exam")
        self.assertIn('Prayer request successfully recorded', output)

        output = self.plugin.send_command("list")
        self.assertIn('exam', output)


    def tearDown(self):
        pass
