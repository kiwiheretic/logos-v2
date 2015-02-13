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
    
    def setUp(self):
        pass
        
        # Load initial test data into test database

        #https://docs.djangoproject.com/en/1.7/topics/testing/tools/#topics-testing-fixtures
        #https://docs.djangoproject.com/en/dev/ref/django-admin/#database-specific-fixtures        
#        fixtures_path = os.path.join(settings.BASE_DIR, 'logos', 'fixtures')
#        fixture_file = os.path.join(fixtures_path, 'testdata.bibles.json.gz')
#        fp = gzip.open(fixture_file)
#        for ii, obj in enumerate(serializers.deserialize("json", fp)):
#            if ii % 500 == 0: print ".",
#            obj.save()
#        print
        ### === Finished loading test data ===
        
    def testVerseLookup(self):
        self.plugin.send_command("John 3 16")
        self.assertIn('John 3:16', self.plugin.output.pop()[2])
        
        self.plugin.send_command("next")
        self.assertIn('John 3:17', self.plugin.output.pop(0)[2])

        
        
