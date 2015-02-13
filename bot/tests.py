# tests

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

        
        
