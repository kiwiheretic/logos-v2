# tests

# Import the plugin you wish to test
from logos.bot_plugin import SystemCoreCommands

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
