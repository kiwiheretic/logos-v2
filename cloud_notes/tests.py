# plugin tests.py
from __future__ import print_function, absolute_import
from .bot_plugin import NotesPlugin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.test import Client
from django.core.urlresolvers import reverse
import datetime
import pytz

# Subclass your test class from LogosTestCase
from bot.testing.utils import LogosTestCase
from .models import Folder, Note

class TestNotes(LogosTestCase):
    # set plugin_class to the actual class
    # of the plugin you wish to test
    plugin_class = NotesPlugin
    
    def setUp(self):
        # create test users
        #  https://docs.djangoproject.com/en/1.8/topics/auth/default/#creating-users
        self.u1 = fred = User.objects.create_user("fred", "fred@nowhere.com", "pass123")
        self.u2 = john = User.objects.create_user("john", "john@nowhere.com", "pass456")
 
    def test_basic_logging(self):
        self.set_nick("fred")
        self.login('pass123')
        self.set_channel('#myroom')
        
        output = self.plugin.send_command("notes on")
        self.assertIn('Note logging turned on', output)        

        output = self.plugin.send_channel_msg("  test note logging")
        self.assertIn('logged to cloud notes', output)        
        
        output = self.plugin.send_command("notes off")
        self.assertIn('logging turned off', output) 
        
        output = self.plugin.send_channel_msg("# test note logging")
        self.assertNotIn('logged to cloud notes', output)  
        
    def test__note_edit_view(self):
        """ Make sure no exceptions occur on get note for editing"""
        client = Client()
        resp = client.login(username = 'fred', password = 'pass123')
        fldr = Folder.objects.get(user = self.u1, name='Main')
        now = datetime.datetime.now(tz=pytz.UTC)
        note = Note(user=self.u1, folder = fldr, created_at = now,
                modified_at = now, title='Test Note', note='note body' )
        note.save()
        note_id = note.id
        response = client.get(reverse('cloud_notes.views.edit_note', args=(note_id,)))

    def test_channel_independence(self):
        self.set_nick("fred")
        self.login('pass123')
        self.set_channel('#myroom')
        
        output = self.plugin.send_command("notes on")
        self.assertIn('Note logging turned on', output)         

        output = self.plugin.send_signal('verse_lookup', {'verses':['John 3:16 For God so loved ...']})
        self.assertIn('verse(s) logged to cloud notes', output) 
        
        output = self.plugin.send_signal('verse_search', {'verses':['John 3:16 For God so loved ...']})
        self.assertIn('verses searched logged to cloud notes', output) 
        
        self.set_channel('#anotherroom')
        output = self.plugin.send_channel_msg("# test note logging")
        self.assertNotIn('logged to cloud notes', output)         

        output = self.plugin.send_signal('verse_lookup', {'verses':['John 3:16 For God so loved ...']})
        self.assertNotIn('verse(s) logged to cloud notes', output) 

        output = self.plugin.send_signal('verse_search', {'verses':['John 3:16 For God so loved ...']})
        self.assertNotIn('verses searched logged to cloud notes', output) 
        
    def tearDown(self):
        print ("deleting test users.")
        self.u1.delete()
        self.u2.delete()    
