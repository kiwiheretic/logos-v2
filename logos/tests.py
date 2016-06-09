# tests
from __future__ import absolute_import

from django.core.urlresolvers import RegexURLPattern, RegexURLResolver
# Import the plugin you wish to test
from logos.bot_plugin import SystemCoreCommands
import re
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User

# Subclass your test class from LogosTestCase
from bot.testing.utils import LogosTestCase

class TestSystemPlugin(LogosTestCase):
    # set plugin_class to the actual class
    # of the plugin you wish to test
    plugin_class = SystemCoreCommands
    
    def setUp(self):
        self.fred = self.create_user('fred', "fred@noemail.com", "password1")
        self.john= self.create_user('john', "john@noemail.com", "password2")
        
    def testGreet(self):
        self.assign_room_permission('fred', self.room, 'set_greeting')
        self.set_nick("fred")
        
        output = self.plugin.send_command("login password1")
        self.assertIn('Login successful', output)  

        output = self.plugin.send_command("set {} greet message \"hello\"".format(self.room))
        self.assertIn('Greet message for {} set to "hello"'.format(self.room), output)
        
    def testNickRename(self):
        self.set_nick("fred")
        output = self.plugin.send_command("login password1")
        self.assertIn('Login successful', output)  

        self.set_nick("john")
        output = self.plugin.send_command("login password2")
        self.assertIn('Login successful', output)  

        logged_in_users = self.get_logged_in_users()
        self.assertIn("john", logged_in_users)
        self.assertIn("fred", logged_in_users)

        self.change_nick("john", "jake")
        logged_in_users = self.get_logged_in_users()
        self.assertIn("jake", logged_in_users)
        self.assertIn("fred", logged_in_users)


    def testSetTrigger(self):
        self.assign_room_permission('fred', self.room, 'change_trigger')
        self.set_nick("fred")
        
        output = self.plugin.send_command("login password1")
        self.assertIn('Login successful', output)  

        output = self.plugin.send_command("set {} trigger \"?\"".format(self.room))
        print(">>>" +output)
        
    def testRoomPermissions(self):

        self.set_nick("fred")
    
        self.assign_room_permission('fred', self.room, 'can_speak')
        self.set_nick("fred")

        output = self.plugin.send_command("say {} Hello".format(self.room))
        self.assertNotIn('Hello', output)
        
        output = self.plugin.send_command("act {} dances".format(self.room))
        self.assertNotIn('dances', output)

        output = self.plugin.send_command("login password1")
        self.assertIn('Login successful', output)  

        output = self.plugin.send_command("say {} Hello".format(self.room))
        self.assertIn('Hello', output)

        output = self.plugin.send_command("act {} dances".format(self.room))
        self.assertIn('dances', output)
                
        output = self.plugin.send_command("set {} trigger \"?\"".format(self.room))
        self.assertIn('not authorised', output)
        
        self.assign_room_permission('fred', self.room, 'change_trigger')
        output = self.plugin.send_command("set {} trigger \"?\"".format(self.room))
        self.assertNotIn('not authorised', output)
        
    def tearDown(self):
        self.fred.delete()
        self.john.delete()

from .urls import urlpatterns as top_urls

class TestUrls(TestCase):
    def setUp(self):
        self.fred = User.objects.create_user('fred', "fred@noemail.com", "password1")

    def strip_regex_chars(self, pattern):
        if not pattern: return ''
        if pattern[0] == '^':
            pattern = pattern[1:]
        if pattern[-1] == '$':
            pattern = pattern[:-1]
        return pattern

    def recursive_get_urls(self, urlpatterns, prefix=''):
        for url in urlpatterns:
            #print type(url)
            #print url.regex.pattern
            if type(url) == RegexURLPattern:
                if re.search(r'\(.*\)', url.regex.pattern):
                    # parametrized urls are not tested yet, maybe a later TODO
                    pass
                else:
                    fetch_url = "/"+prefix+self.strip_regex_chars(url.regex.pattern)
                    print fetch_url
                    if fetch_url.startswith('/admin/') or \
                        fetch_url.startswith('/auth/') or \
                        fetch_url.startswith('/sites/'):
                        pass
                    else:
                        resp = self.c.get(fetch_url)
                        print resp.status_code

            elif type(url) == RegexURLResolver:
                anchor_prefix = self.strip_regex_chars(url.regex.pattern)
                #print url.url_patterns
                self.recursive_get_urls(url.url_patterns, prefix = anchor_prefix)

    def test_get_urls_accessible(self, prefex = ''):
        self.c = Client()
        self.c.login(username='fred', password='password1')
        self.recursive_get_urls(top_urls)

    def tearDown(self):
        self.fred.delete()
