from plugins.cloud_memos.plugin import MemosPlugin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
# Subclass your test class from LogosTestCase
from bot.testing.utils import LogosTestCase

class TestMemos(LogosTestCase):
    # set plugin_class to the actual class
    # of the plugin you wish to test
    plugin_class = MemosPlugin
 
    
    def setUp(self):
        # create test users
        #  https://docs.djangoproject.com/en/1.8/topics/auth/default/#creating-users
        self.u1 = fred = User.objects.create_user("fred", "fred@nowhere.com", "pass123")
        self.u2 = john = User.objects.create_user("john", "john@nowhere.com", "pass456")
        self.u3 = mary = User.objects.create_user("mary", "mary@nowhere.com", "Pass789")
 
 
    def testMemoSend(self):
        
        self.set_nick("fred")
        self.login('pass123')
        
        output = self.plugin.send_command("send john Hi, How are you")
        self.assertIn('Memo sent', output)

        self.set_nick("john")
        self.login("pass456")
        output = self.plugin.send_command("check")
        self.assertIn('1 unread', output)
        
        output = self.plugin.send_command("read 0")
        self.assertIn('How are you', output)
        
        output = self.plugin.send_command("check")
        self.assertIn('no unread', output)
        
        output = self.plugin.send_command("delete 0")
        self.assertIn('deleted', output)
        
        output = self.plugin.send_command("list")
        self.assertIn('No memos found', output)

        output = self.plugin.send_command("send Mary Hi, How are you")
        self.assertIn('Memo sent', output)

        self.set_nick("Mary")
        self.login("Pass789")
        output = self.plugin.send_command("check")
        self.assertIn("You have 1 unread memos", output)
        
    def tearDown(self):
        print ("deleting test users.")
        self.u1.delete()
        self.u2.delete()
        self.u3.delete()