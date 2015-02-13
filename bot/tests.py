# tests

# Helper modules to load in some fixture data which in this
# case is a small amount of bible data KJV gospels only along 
# with concordance data.
from django.conf import settings
from django.core import serializers
import gzip
import os
import pdb

# Import the plugin you wish to test
from bot.plugins.bible_bot import BibleBot

# Subclass your test class from LogosTestCase
from bot.testing.utils import LogosTestCase

class TestBibleBot(LogosTestCase):
    # set plugin_class to the actual class
    # of the plugin you wish to test
    plugin_class = BibleBot
    
    def testVerseLookup(self):
        output = self.plugin.send_command("John 3 16")
        self.assertIn('John 3:16', output)
        
        output = self.plugin.send_command("next")
        self.assertIn('John 3:17', output)

        
        
